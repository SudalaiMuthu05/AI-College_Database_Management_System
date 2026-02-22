import psycopg2
import psycopg2.pool
import requests
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# =========================
# DATABASE CONFIG
# =========================
DB_CONFIG = {
    "host": "localhost",
    "database": "student_db",
    "user": "postgres",
    "password": "5342",
    "port": "5432"
}

TABLE_NAME = "students"   # This is now a VIEW over 3 partitions
DEFAULT_LIMIT = 50
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral"

# =========================
# CONNECTION POOL (FASTER)
# =========================
connection_pool = psycopg2.pool.SimpleConnectionPool(
    1, 10, **DB_CONFIG
)

# =========================
# CLEAN SQL OUTPUT
# =========================
def clean_sql_output(raw_output):
    if not raw_output:
        return None

    raw_output = raw_output.replace("```sql", "").replace("```", "").strip()

    match = re.search(r"(select[\s\S]+)", raw_output, re.IGNORECASE)
    if not match:
        return None

    sql = match.group(1).split(";")[0].strip()

    # Force correct table name
    sql = re.sub(r"\bstudent\b", TABLE_NAME, sql, flags=re.IGNORECASE)

    # Add LIMIT only if not aggregation
    if (
        "limit" not in sql.lower()
        and "count(" not in sql.lower()
        and "avg(" not in sql.lower()
        and "sum(" not in sql.lower()
    ):
        sql += f" LIMIT {DEFAULT_LIMIT}"

    return sql


# =========================
# GENERATE SQL FROM OLLAMA
# =========================
def generate_sql(question):

    prompt = f"""
You are an expert PostgreSQL query generator.

Database schema:

Table: students

Columns:
- student_id
- student_name
- date_of_birth
- field_of_study
- year_of_admission
- expected_year_of_graduation
- current_semester
- specialization
- fees

STRICT RULES:
- Output ONLY raw SQL.
- Start directly with SELECT.
- Do NOT explain anything.
- Never generate INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE.
- Always use table name students.
- Use ILIKE for text search.
- If asking for person details, use:
  student_name ILIKE '%name%'.
- Default LIMIT 50 if not specified.

User question:
{question}
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0}
            },
            timeout=60
        )

        raw_output = response.json().get("response", "")
        print("\nRAW LLM OUTPUT:\n", raw_output)

        return clean_sql_output(raw_output)

    except Exception as e:
        print("Ollama Error:", e)
        return None


# =========================
# EXECUTE QUERY (POOL BASED)
# =========================
def execute_query(sql_query):
    conn = connection_pool.getconn()
    try:
        cursor = conn.cursor()
        cursor.execute(sql_query)
        column_names = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        cursor.close()
        return [dict(zip(column_names, row)) for row in rows]
    finally:
        connection_pool.putconn(conn)


# =========================
# STRICT SQL VALIDATION
# =========================
def validate_sql(sql_query):
    if not re.match(r"^\s*select\b", sql_query, re.IGNORECASE):
        return False

    forbidden = ["insert", "update", "delete", "drop", "alter", "truncate"]
    if any(word in sql_query.lower() for word in forbidden):
        return False

    return True


# =========================
# CHAT ROUTE
# =========================
@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()
    user_question = data.get("message")

    if not user_question:
        return jsonify({"error": "No question provided"}), 400

    sql_query = generate_sql(user_question)

    if not sql_query:
        return jsonify({"error": "Failed to generate SQL"}), 500

    if not validate_sql(sql_query):
        return jsonify({"error": "Unsafe query blocked"}), 400

    try:
        result = execute_query(sql_query)

        return jsonify({
            "sql": sql_query,
            "result": result,
            "row_count": len(result),
            "corrected": False
        })

    except Exception as e:
        print("SQL ERROR:", e)

        # =========================
        # SELF-CORRECTION LOOP
        # =========================
        fix_prompt = f"""
The following SQL query caused an error:

{sql_query}

Error:
{str(e)}

Fix the SQL. Return only corrected SELECT query.
"""

        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": MODEL_NAME,
                    "prompt": fix_prompt,
                    "stream": False,
                    "options": {"temperature": 0}
                }
            )

            raw_fix = response.json().get("response", "")
            fixed_sql = clean_sql_output(raw_fix)

            if not fixed_sql or not validate_sql(fixed_sql):
                return jsonify({"error": "Query failed and could not fix"}), 500

            result = execute_query(fixed_sql)

            return jsonify({
                "sql": fixed_sql,
                "result": result,
                "row_count": len(result),
                "corrected": True
            })

        except Exception as inner_error:
            return jsonify({
                "error": str(inner_error),
                "original_sql": sql_query
            }), 500


# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    app.run(debug=True)