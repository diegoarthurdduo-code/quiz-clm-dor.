import streamlit as st
import json, random, time, io, html
from pathlib import Path
import qrcode

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="CLM D'OR • Quiz Vape", page_icon="🌿", layout="centered")
st.markdown("""<style>
.stApp {background: #082520; color: #f0fff8;}
.block-container {max-width: 760px; padding-top: 2rem; padding-bottom: 3rem;}
h1,h2,h3 {color: #73E3BA !important;}
[data-testid="stForm"] {background:#123d32; border:1px solid #29745c; border-radius:24px; padding:24px;}
.stButton button,.stFormSubmitButton button {border-radius:18px; min-height:50px;}
[data-testid="stRadio"] {background:#164536; padding:18px; border-radius:20px;}
[data-testid="stRadio"] label {white-space:normal;}
.hero {text-align:center; padding:20px 0;}
.hero p {color:#bee4d4;}
@media(max-width:600px){.block-container{padding:1rem;} h1{font-size:1.9rem!important;}}
</style>""", unsafe_allow_html=True)
logo = ROOT / "hospital.png"
if logo.exists():
    left, center, right = st.columns([1,2,1])
    with center: st.image(str(logo), use_container_width=True)
st.markdown("<div class='hero'><h1>Quiz Vape</h1><p>CLM D'OR • Conhecimento que cuida de você</p></div>", unsafe_allow_html=True)

s = st.session_state
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
    st.subheader("Seu próximo conhecimento começa aqui")
    st.write("10 perguntas sobre cigarros eletrônicos. Escolha uma alternativa e confirme para ver a explicação.")
    with st.form("entry"):
        name = st.text_input("Como podemos te chamar?", max_chars=60, placeholder="Digite seu nome ou apelido")
        submitted = st.form_submit_button("Começar quiz", use_container_width=True, type="primary")
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
        st.subheader(q["prompt"])
        choice = st.radio("Selecione sua resposta:", range(4), index=None,
            format_func=lambda i: f"{'ABCD'[i]}. {q['options'][i]}",
            key=f"answer_{s.index}", disabled=s.feedback is not None)
        if s.feedback is None:
            if st.button("Confirmar resposta", type="primary", use_container_width=True):
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
                    type="primary", use_container_width=True):
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
        file_name="resultado_quiz.json", mime="application/json", use_container_width=True)
    if st.button("Jogar novamente", use_container_width=True):
        s.clear(); st.rerun()

with st.sidebar:
    st.header("QR Code da feira")
    st.caption("Depois de publicar, cole o endereço público do quiz abaixo.")
    url = st.text_input("Link publicado", placeholder="https://seu-quiz.streamlit.app")
    if url.startswith("https://"):
        buffer = io.BytesIO()
        qrcode.make(url).save(buffer,format="PNG")
        st.image(buffer.getvalue(), caption="Escaneie para participar")
        st.download_button("Baixar QR Code", buffer.getvalue(), "qr_quiz.png", "image/png")
    elif url: st.warning("Use o endereço completo, começando com https://")
