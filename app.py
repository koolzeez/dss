from flask import Flask, render_template, request, redirect, url_for, session
from experta import KnowledgeEngine, Fact, Rule, MATCH, TEST, DefFacts

app = Flask(__name__)
app.secret_key = 'supersecretkey_production'

# ---------- FACT ----------
class CropDiagnosis(Fact):
    """Fact to hold all the crop symptoms."""
    pass

# ---------- ENGINE ----------
class TuberDSS(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.results = []

    @DefFacts()
    def _initial_action(self):
        yield Fact(action="diagnose")

    # --- YAM ANTHRACNOSE RULES ---
    @Rule(CropDiagnosis(cnn="Yam Anthracnose", leaf_texture="dry_brittle", stem_lesion="wet", tuber_firmness="soft_mushy", tuber_smell="foul"))
    def ya_high(self):
        self.results.append("""HIGH LIKELIHOOD: Yam Anthracnose|This is a severe infection. Immediate action is required:
- **Sanitation:** Carefully prune and collect all infected leaves, stems, and tubers. Do not compost them. The best method of disposal is burning. If not possible, bury them at least 2 feet deep.
- **Fungicide Application:** Apply a protective fungicide like Mancozeb or a copper-based product. Ensure full coverage of all plant surfaces. Follow the manufacturer's instructions for dosage and frequency.
- **Crop Rotation:** Do not plant yams in this field for at least 2-3 years. Rotate with non-host crops like maize, legumes, or sorghum.""")

    @Rule(CropDiagnosis(cnn="Yam Anthracnose", stem_lesion="wet", leaf_texture=MATCH.lt, tuber_firmness=MATCH.tf),
          TEST(lambda lt, tf: lt == "dry_brittle" or tf == "soft_mushy"))
    def ya_mod(self):
        self.results.append("""MODERATE LIKELIHOOD: Yam Anthracnose|The disease is present and needs to be managed:
- **Immediate Action:** Remove and destroy all visibly affected plant parts to reduce the spread of spores.
- **Fungicide:** Consider applying a recommended fungicide, especially if weather conditions are wet and humid, which favors the disease.
- **Monitoring:** Inspect your plants twice a week. Look for new lesions on leaves and stems. If symptoms spread, escalate to the high-likelihood control measures.""")

    @Rule(CropDiagnosis(cnn="Yam Anthracnose", leaf_texture="dry_brittle", stem_lesion="no", tuber_firmness="normal_firm"))
    def ya_low(self):
        self.results.append("""LOW LIKELIHOOD: Yam Anthracnose|Symptoms are minor but should not be ignored:
- **Isolate & Observe:** Remove the few affected leaves.
- **Improve Airflow:** Ensure there is good spacing between plants to reduce humidity. Prune any unnecessary foliage.
- **Withhold Fungicide:** Hold off on chemical sprays for now, but be prepared to act if the disease spreads. This could also be sun scorch; ensure consistent watering.""")

    # --- YAM MOSAIC VIRUS RULES ---
    @Rule(CropDiagnosis(cnn="Yam Mosaic Virus", leaf_texture="normal_soft_puckered", tuber_firmness="normal_firm"))
    def ymv_high(self):
        self.results.append("""HIGH LIKELIHOOD: Yam Mosaic Virus|This viral disease is spread by aphids and infected materials. There is no cure, so prevention of spread is key:
- **Roguing:** Immediately and carefully uproot the entire infected plant. Place it in a bag on the spot to avoid shaking aphids off, and remove it from the field. Burn or bury it deeply.
- **Vector Control:** Control the aphid population. Options include spraying with insecticidal soap or neem oil, or encouraging natural predators like ladybugs.
- **Clean Planting Material:** For your next crop, source certified virus-free yam setts from a reputable agricultural institution.""")

    @Rule(CropDiagnosis(cnn="Yam Mosaic Virus", leaf_texture="normal_soft_puckered", tuber_firmness="soft_mushy"))
    def ymv_mod_rot(self):
        self.results.append("""MODERATE LIKELIHOOD: Yam Mosaic Virus with secondary tuber rot|The primary issue is the virus, which may have weakened the plant and allowed for a secondary rot infection:
- **Primary Control:** Uproot and destroy the infected plant to prevent the virus from spreading.
- **Storage Management:** The tuber rot suggests issues with soil moisture or storage. Improve soil drainage. When harvesting, cure tubers in a dry, airy location for several days before long-term storage.""")

    # --- CASSAVA BACTERIAL BLIGHT RULES ---
    @Rule(CropDiagnosis(cnn="Cassava Bacterial Blight", leaf_texture="soft_mushy", stem_sticky="yes", tuber_firmness="soft_mushy", tuber_smell="foul"))
    def cbb_high(self):
        self.results.append("""HIGH LIKELIHOOD: Cassava Bacterial Blight|This is a very serious and contagious bacterial disease. Strict quarantine and sanitation are critical:
- **Total Destruction:** Uproot and burn all infected plants immediately. Do not leave any debris in the field.
- **Tool Sterilization:** Thoroughly disinfect all tools (machetes, hoes, etc.) used in the affected area with a 10% bleach solution (1 part bleach to 9 parts water).
- **Field Quarantine:** Do not plant cassava in this field for at least two full growing seasons.
- **Resistant Varieties:** In the future, plant varieties known to be resistant to CBB.""")

    @Rule(CropDiagnosis(cnn="Cassava Bacterial Blight", stem_sticky="yes", leaf_texture=MATCH.lt, tuber_firmness=MATCH.tf),
          TEST(lambda lt, tf: lt == "soft_mushy" or tf == "soft_mushy"))
    def cbb_mod(self):
        self.results.append("""MODERATE LIKELIHOOD: Cassava Bacterial Blight|The presence of sticky ooze is a major red flag. Act now to prevent a full-blown outbreak:
- **Sanitation:** Begin by removing and burning any plants showing symptoms.
- **Tool Discipline:** Start a strict tool disinfection routine for all farm activities. Do not move from affected areas to healthy areas without cleaning tools first.
- **Monitoring:** Check your field daily for new symptoms like angular leaf spots, wilting, or dieback.""")
    
    @Rule(CropDiagnosis(cnn="Cassava Bacterial Blight", leaf_texture="soft_mushy", stem_sticky="no"))
    def cbb_low(self):
        self.results.append("""LOW LIKELIHOOD: Cassava Bacterial Blight|The key symptom (sticky stem) is absent, but caution is needed:
- **Water Management:** Soft leaves can be caused by waterlogged soil. Check soil moisture and ensure proper drainage.
- **Vigilant Monitoring:** Watch the plants closely for a week. If you see any gummy liquid on stems or angular, water-soaked spots on leaves, escalate to moderate-level controls immediately.""")


    # --- CASSAVA MOSAIC VIRUS RULES ---
    @Rule(CropDiagnosis(cnn="Cassava Mosaic Virus", leaf_texture="normal_soft_puckered", tuber_firmness="normal_firm"))
    def cmv_high(self):
        self.results.append("""HIGH LIKELIHOOD: Cassava Mosaic Virus|Similar to YMV, this is a viral disease with no cure. Control is focused on stopping the vector (whitefly) and using clean material:
- **Roguing:** Uproot and destroy any plant showing the characteristic mosaic and distorted leaves.
- **Vector Control:** Manage whitefly populations. Use yellow sticky traps to monitor and catch them. Applications of neem oil can deter feeding.
- **Clean Cuttings:** Only plant cuttings taken from healthy, symptom-free mother plants. If possible, use certified virus-free cuttings.""")

    @Rule(CropDiagnosis(cnn="Cassava Mosaic Virus", leaf_texture="normal_soft_puckered", tuber_firmness="soft_mushy"))
    def cmv_mod_rot(self):
        self.results.append("""MODERATE LIKELIHOOD: Cassava Mosaic Virus with tuber rot|The virus has likely weakened the plant, making it susceptible to other soil-borne pathogens:
- **Address the Virus First:** Remove and destroy the mosaic-infected plants to stop the virus from spreading via whiteflies.
- **Investigate Rot:** Check for causes of rot. Is the soil poorly drained? Were tubers damaged during weeding? Address these underlying issues to protect healthy plants.""")

    # --- CONFLICTING / OVERRIDE RULES (High Salience) ---
    @Rule(CropDiagnosis(cnn="Healthy", stem_sticky="yes"), salience=10)
    def override_cbb_critical(self):
        self.results.append("""CRITICAL: Cassava Bacterial Blight (Symptom Override)|The CNN result has been overridden. A sticky stem is a definitive sign of Bacterial Blight.
- **Urgent Action:** Do not trust the 'Healthy' scan. Treat this as a high-likelihood CBB infection. Immediately uproot and burn the plant. Sterilize any tool that touched it. This symptom is too critical to ignore.""")

    @Rule(CropDiagnosis(cnn="Healthy", leaf_texture="normal_soft_puckered"), salience=9)
    def override_mosaic(self):
        self.results.append("""POSSIBLE: Mosaic Virus (Symptom Override)|The leaf puckering is a classic symptom of a mosaic virus that should not be ignored, even if the CNN scan indicated 'Healthy'.
- **Precautionary Measures:** It is safest to assume the plant is infected. Uproot and destroy it to prevent spread by insect vectors (aphids for yam, whiteflies for cassava).""")

    @Rule(CropDiagnosis(cnn="Yam Anthracnose", leaf_texture="normal_soft_puckered"), salience=8)
    def conflict_ya_ymv(self):
        self.results.append("""INCONCLUSIVE: Conflicting Information|The system cannot make a reliable diagnosis.
- **Reason:** The CNN scan suggests a fungal disease (Anthracnose), but the physical symptoms strongly point to a viral disease (Mosaic Virus).
- **Recommendation:** Do not apply any chemical treatments yet. Isolate the plant if possible and seek advice from a local agricultural extension officer for a definitive identification.""")

    # --- HEALTHY / ABIOTIC STRESS RULES ---
    @Rule(CropDiagnosis(cnn="Healthy", leaf_texture="normal_firm", stem_lesion="no", stem_sticky="no", tuber_texture="smooth", tuber_firmness="normal_firm", tuber_smell="mild"))
    def healthy_plant(self):
        self.results.append("""Likely Healthy|All signs point to a healthy plant. Maintain your excellent work by continuing good agricultural practices:
- **Weed Management:** Keep the area around the plant base clear of weeds that compete for nutrients and water.
- **Soil Health:** Ensure good drainage and consider mulching to conserve soil moisture.
- **Regular Scouting:** Continue to walk through your fields weekly to catch any potential issues early.""")

    @Rule(CropDiagnosis(cnn="Healthy", leaf_texture="dry_brittle", stem_lesion="no", tuber_firmness="normal_firm"))
    def abiotic_stress(self):
        self.results.append("""Likely Healthy with Minor Abiotic Stress|No disease was detected. The symptoms are likely due to environmental factors:
- **Water Stress:** Check the soil moisture. The leaves may be dry due to inconsistent watering. Ensure the crop gets adequate water, especially during dry spells.
- **Sun Scorch:** If the dry spots are mainly on leaves exposed to direct, intense sunlight, it could be sun scorch. If this is a persistent problem, consider intercropping with taller plants to provide partial shade.""")

    # --- FALLBACK RULE (Lowest Salience) ---
    @Rule(salience=-1)
    def fallback(self):
        if not self.results:
            self.results.append("""INCONCLUSIVE: No Clear Match|The combination of symptoms provided does not match a specific disease profile in the knowledge base.
- **Next Step:** For an accurate diagnosis, it is highly recommended to take clear photos and consult a local agricultural extension officer or a plant pathology lab.""")


# ---------- FLASK ROUTES (No changes needed below) ----------
@app.route('/')
def index():
    session.clear()
    return render_template('index.html')

@app.route('/step1_cnn', methods=['GET', 'POST'])
def step1_cnn():
    if request.method == 'POST':
        session['cnn'] = request.form['cnn']
        return redirect(url_for('step1_leaf'))
    return render_template('step1_cnn.html')

@app.route('/step1_leaf', methods=['GET', 'POST'])
def step1_leaf():
    if 'cnn' not in session: return redirect(url_for('step1_cnn'))
    if request.method == 'POST':
        session['leaf_texture'] = request.form['leaf_texture']
        return redirect(url_for('step2'))
    return render_template('step1_leaf.html')

@app.route('/step2', methods=['GET', 'POST'])
def step2():
    if 'leaf_texture' not in session: return redirect(url_for('step1_leaf'))
    if request.method == 'POST':
        session['stem_lesion'] = request.form.get('stem_lesion', 'no')
        session['stem_sticky'] = request.form.get('stem_sticky', 'no')
        return redirect(url_for('step3_texture'))
    cnn_result = session.get('cnn')
    return render_template('step2.html', cnn_result=cnn_result)

@app.route('/step3_texture', methods=['GET', 'POST'])
def step3_texture():
    if 'stem_lesion' not in session: return redirect(url_for('step2'))
    if request.method == 'POST':
        session['tuber_texture'] = request.form['tuber_texture']
        return redirect(url_for('step3_firmness'))
    return render_template('step3_texture.html')

@app.route('/step3_firmness', methods=['GET', 'POST'])
def step3_firmness():
    if 'tuber_texture' not in session: return redirect(url_for('step3_texture'))
    if request.method == 'POST':
        session['tuber_firmness'] = request.form['tuber_firmness']
        return redirect(url_for('step3_smell'))
    return render_template('step3_firmness.html')

@app.route('/step3_smell', methods=['GET', 'POST'])
def step3_smell():
    if 'tuber_firmness' not in session: return redirect(url_for('step3_firmness'))
    if request.method == 'POST':
        session['tuber_smell'] = request.form['tuber_smell']

        engine = TuberDSS()
        engine.reset()
        engine.declare(CropDiagnosis(
            cnn=session.get('cnn'),
            leaf_texture=session.get('leaf_texture'),
            stem_lesion=session.get('stem_lesion'),
            stem_sticky=session.get('stem_sticky'),
            tuber_texture=session.get('tuber_texture'),
            tuber_firmness=session.get('tuber_firmness'),
            tuber_smell=session.get('tuber_smell'),
        ))
        engine.run()
        session['results'] = engine.results
        return redirect(url_for('result_page'))
    return render_template('step3_smell.html')

@app.route('/result')
def result_page():
    if 'results' not in session: return redirect(url_for('index'))
    results = session.get('results', ["INCONCLUSIVE|No result found. Please start over."])
    return render_template('result.html', result_list=results)

if __name__ == '__main__':
    app.run(debug=True)
