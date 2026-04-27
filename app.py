from google import genai
from google.genai import types

app = Flask(__name__)

API_KEY = os.environ.get("GEMINI_API_KEY", "")

PROMPT = """You are an expert zoologist and wildlife encyclopedia AI.
Analyze this animal photo and respond ONLY with a valid JSON object (no markdown, no code fences, no extra text).
Use exactly these fields:
{
  "common_name": "string",
  "scientific_name": "string",
  "kingdom": "string",
  "class": "string",
  "order": "string",
  "region": "string (countries or continents where this animal is found)",
  "habitat": "string (detailed habitat description)",
  "length_height": "string (body size)",
  "weight": "string",
  "diet": "string",
  "lifespan": "string",
  "conservation_status": "string (Least Concern / Vulnerable / Endangered / Critically Endangered / Extinct in the Wild / Extinct)",
  "interesting_fact": "string (one fascinating fact)",
  "confidence": "string (High / Medium / Low)"
}
If the image does not contain an animal, set common_name to "Not an Animal" and all other fields to "N/A"."""


@app.route("/")
def index():
    if not API_KEY:
        return render_template("index.html", api_key_missing=True)
    return render_template("index.html", api_key_missing=False)


@app.route("/identify", methods=["POST"])
def identify():
    if not API_KEY:
        return jsonify({"error": "GEMINI_API_KEY is not set."}), 500

    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    image_data = file.read()
    media_type = file.content_type or "image/jpeg"

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
response = model.generate_content([
    {"mime_type": media_type, "data": image_data},
    PROMPT
])

        text = response.text.strip()
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        animal_data = json.loads(text)
        return jsonify(animal_data)

    except json.JSONDecodeError:
        return jsonify({"error": "Could not parse AI response. Please try again."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    if not API_KEY:
        print("\n⚠️  WARNING: GEMINI_API_KEY is not set!")
        print("Set it with:  $env:GEMINI_API_KEY=\"your-key-here\"  (PowerShell)")
        print("Then restart the app.\n")
    else:
        print("\n✅ Gemini API key found! Starting WildLens...\n")
    port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
