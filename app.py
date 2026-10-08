import streamlit as st
import json, random, time, io, html
from pathlib import Path
import qrcode

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="CLM D'OR • QUIZ ENF", page_icon="🌿", layout="centered", initial_sidebar_state="collapsed")
st.markdown("""<style>
.stApp {background:radial-gradient(ellipse at top right,#174d43 0%,#091f1d 50%,#061512 100%);color:#fff;}
.block-container {max-width:850px;padding-top:2.3rem;padding-bottom:3rem;}
header[data-testid="stHeader"] {background:transparent;}
h1,h2,h3 {color:#ffffff!important;}
[data-testid="stMarkdownContainer"] p {color:#e3f1ed;font-size:18px;line-height:1.65;}
[data-testid="stCaptionContainer"] p {color:#a8c7bb!important;font-size:14px;}
[data-testid="stForm"], [data-testid="stVerticalBlockBorderWrapper"]>div {background:rgba(16,48,41,.85);border:1px solid #2c6857!important;border-radius:28px!important;padding:24px;box-shadow:0 18px 45px #0003;}
.stButton button,.stFormSubmitButton button,.stDownloadButton button {border-radius:16px;min-height:55px;border:1px solid #3b806a;background:#133f33;color:white;}
button[kind="primary"],button[kind="primaryFormSubmit"] {background:linear-gradient(115deg,#20916d,#66d6a5)!important;border:none!important;color:#052419!important;box-shadow:0 8px 24px #34c99625;}
button p {font-size:17px!important;font-weight:700!important;color:inherit!important;}
[data-testid="stTextInput"] input {background:#081e18;color:white;font-size:18px;min-height:52px;border-radius:12px;}
[data-testid="stRadio"] {padding:8px 0;}
[data-testid="stRadio"] [role="radiogroup"] {gap:12px;}
[data-testid="stRadio"] label[data-baseweb="radio"] {background:#102d25;border:1px solid #355a4b;border-radius:16px;padding:16px!important;width:100%;margin:0!important;align-items:flex-start;transition:background .2s;}
[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) {background:#20583e;border-color:#70e3a8;box-shadow:0 0 0 1px #70e3a8;}
[data-testid="stRadio"] label p {font-size:19px!important;color:#fff!important;line-height:1.5!important;}
[data-testid="stRadio"] label {white-space:normal;opacity:1!important;}
[data-testid="stSidebar"] {background:#0b211c;border-right:1px solid #315d4d;}
.hero {text-align:center;padding:12px 0 28px;}
.hero h1 {font-size:52px!important;font-weight:850;letter-spacing:3px;margin:0;}
.hero .eyebrow {font-size:12px;color:#85ddba;letter-spacing:3px;font-weight:700;}
.hero p {color:#b6d8cb!important;font-size:16px!important;}
.question {color:#fff!important;font-size:30px!important;line-height:1.4!important;font-weight:750;margin:10px 0 25px;}
.intro {font-size:32px;font-weight:750;color:white;line-height:1.25;margin-bottom:12px;}
.stats {display:flex;gap:12px;margin:12px 0 22px;}
.stat {flex:1;background:#123b2e;border:1px solid #315f4a;border-radius:16px;padding:14px;text-align:center;color:#d8eee3;}
.stat strong {display:block;font-size:25px;color:#83e1b4;}
[data-testid="stMetricValue"] {color:#8fe4b8;}
@media(max-width:600px){.block-container{padding:1rem;} .hero h1{font-size:39px!important;} .question{font-size:25px!important;} .intro{font-size:27px;} [data-testid="stRadio"] label p{font-size:18px!important;} [data-testid="stForm"]{padding:18px!important;}}
</style>""", unsafe_allow_html=True)
logo = ROOT / "hospital.png"
if logo.exists():
    left, center, right = st.columns([1,2,1])
    with center: st.image(str(logo), width="stretch")
st.markdown("<div class='hero'><span class='eyebrow'>CLM D’OR • FEIRA ESCOLAR</span><h1>QUIZ ENF</h1><p>Aprenda. Responda. Descubra.</p></div>", unsafe_allow_html=True)

s = st.session_state
if s.get("app_version") != 2:
    s.clear()
    s.app_version = 2
    s.phase = "login"
if "phase" not in s: s.phase = "login"

def start(name):
    questions = json.loads((ROOT / "perguntas.json").read_text(encoding="utf-8"))
    random.shuffle(questions)
    for q in questions:
        correct = q["options"][q["correct_index"]]
        random.shuffle(q["options"])
        q["correct_index"] = q["options"].index(correct)
    s.questions = questions
    s.name = name
    s.index = 0
    s.answers = []
    s.feedback = None
    s.started = time.time()
    s.phase = "quiz"

if s.phase == "login":
    st.markdown("<div class='intro'>Um desafio para quem<br>cuida do futuro.</div>", unsafe_allow_html=True)
    st.markdown("<div class='stats'><div class='stat'><strong>10</strong>perguntas</div><div class='stat'><strong>A–D</strong>alternativas</div><div class='stat'><strong>100%</strong>aprendizado</div></div>", unsafe_allow_html=True)
    st.write("10 perguntas sobre cigarros eletrônicos. Escolha uma alternativa e confirme para ver a explicação.")
    with st.form("entry"):
        name = st.text_input("Como podemos te chamar?", max_chars=60, placeholder="Digite seu nome ou apelido")
        submitted = st.form_submit_button("Começar quiz", width="stretch", type="primary")
    if submitted:
        if name.strip():
            start(name.strip()); st.rerun()
        else: st.warning("Digite seu nome ou apelido para começar.")
    st.caption("Participação escolar. Sem criação de conta ou senha. O resultado fica nesta sessão e pode ser baixado no final.")

elif s.phase == "quiz":
    st.write(f"Participante: {s.name}")
    st.progress(s.index / len(s.questions))
    st.caption(f"Pergunta {s.index + 1} de {len(s.questions)} • {sum(a['correct'] for a in s.answers)} acertos")
    q = s.questions[s.index]
    with st.container(border=True):
        st.markdown(f'<div class="question">{html.escape(q["prompt"])}</div>', unsafe_allow_html=True)
        choice = st.radio("Selecione sua resposta:", range(4), index=None,
            format_func=lambda i: f"{'ABCD'[i]}. {q['options'][i]}",
            key=f"answer_{s.index}", disabled=s.feedback is not None)
        if s.feedback is None:
            if st.button("Confirmar resposta", type="primary", width="stretch"):
                if choice is None: st.warning("Selecione uma alternativa antes de confirmar.")
                else:
                    correct = choice == q["correct_index"]
                    s.answers.append({"question":q["prompt"], "selected":q["options"][choice],
                        "correct_answer":q["options"][q["correct_index"]], "correct":correct,
                        "explanation":q["explanation"]})
                    s.feedback = correct
                    st.rerun()
        else:
            if s.feedback: st.success("Você acertou!")
            else: st.error("Essa não é a alternativa correta.")
            st.info("Resposta correta: " + q["options"][q["correct_index"]])
            st.write(q["explanation"])
            if st.button("Ver resultado" if s.index == len(s.questions)-1 else "Próxima pergunta",
                    type="primary", width="stretch"):
                s.index += 1
                s.feedback = None
                if s.index == len(s.questions):
                    s.elapsed = int(time.time()-s.started)
                    s.phase = "result"
                st.rerun()

elif s.phase == "result":
    score = sum(a["correct"] for a in s.answers)
    total = len(s.questions)
    st.subheader(f"Parabéns pela participação, {s.name}!")
    st.metric("Seu resultado", f"{score}/{total}")
    st.progress(score/total)
    level = "Excelente conhecimento" if score >= 8 else "Bom caminho" if score >= 5 else "Continue aprendendo"
    st.success(level)
    st.write(f"Tempo: {s.elapsed//60} min {s.elapsed%60} s")
    st.write("Use as explicações para revisar o que aprendeu e compartilhar conhecimento.")
    for i, a in enumerate(s.answers, 1):
        with st.expander(f"{i}. {'Acertou' if a['correct'] else 'Revisar'} — {a['question']}"):
            st.write("Sua resposta: " + a["selected"])
            st.write("Resposta correta: " + a["correct_answer"])
            st.write(a["explanation"])
    report = {"participant":s.name,"score":score,"total":total,"seconds":s.elapsed,"answers":s.answers}
    st.download_button("Baixar meu resultado", json.dumps(report,ensure_ascii=False,indent=2),
        file_name="resultado_quiz.json", mime="application/json", width="stretch")
    if st.button("Jogar novamente", width="stretch"):
        s.clear(); st.rerun()

with st.sidebar:
    st.header("QR Code da feira")
    st.caption("Depois de publicar, cole o endereço público do quiz abaixo.")
    url = st.text_input("Link publicado", placeholder="https://seu-quiz.streamlit.app").strip()
    if url.startswith("https://"):
        buffer = io.BytesIO()
        qrcode.make(url).save(buffer,format="PNG")
        st.image(buffer.getvalue(), caption="Escaneie para participar")
        st.download_button("Baixar QR Code", buffer.getvalue(), "qr_quiz.png", "image/png")
    elif url: st.warning("Use o endereço completo, começando com https://")
