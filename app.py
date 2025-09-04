import streamlit as st
import google.generativeai as genai
import os

# ==============================================================================
# PENGATURAN API KEY DAN MODEL (PENTING! UBAH SESUAI KEBUTUHAN ANDA)
# ==============================================================================

# Mengambil API Key dari Streamlit Secrets atau environment variable
# Ini cara yang aman untuk menyembunyikan API Key di GitHub
# Petunjuk: Buat file .streamlit/secrets.toml dan isi [genai_api] key = "API_KEY_ANDA"
try:
    API_KEY = st.secrets["genai_api"]["key"]
except KeyError:
    API_KEY = os.getenv("GEMINI_API_KEY")
    if not API_KEY:
        st.error("API Key Gemini tidak ditemukan. Harap tambahkan ke Streamlit Secrets atau environment variables.")
        st.stop()

# Nama model Gemini yang akan digunakan.
MODEL_NAME = 'gemini-1.5-flash'

# ==============================================================================
# KONTEKS AWAL CHATBOT (INI BAGIAN YANG BISA SISWA MODIFIKASI!)
# ==============================================================================

# Definisikan peran chatbot Anda di sini.
INITIAL_CHATBOT_CONTEXT = [
    {
        "role": "user",
        "parts": ["Kamu adalah seorang Budayawan. Tuliskan tentang kebudayaan yang ingin diketahui. Jawaban singkat dan faktual. Tolak pertanyaan selain budaya."]
    },
    {
        "role": "model",
        "parts": ["Baik! Saya akan menjawab tentang budaya!."]
    }
]

# ==============================================================================
# FUNGSI UTAMA STREAMLIT
# ==============================================================================

# Judul aplikasi Streamlit
st.title("🤖 Chatbot Budaya")
st.write("Tanyakan apa saja tentang kebudayaan! ✨")

# Konfigurasi API dan model
try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(
        MODEL_NAME,
        generation_config=genai.types.GenerationConfig(
            temperature=0.4,
            max_output_tokens=500
        )
    )
except Exception as e:
    st.error(f"Kesalahan saat mengkonfigurasi atau menginisialisasi model: {e}")
    st.stop()

# Inisialisasi riwayat chat di Streamlit session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = INITIAL_CHATBOT_CONTEXT

if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=st.session_state.chat_history)

# Tampilkan riwayat chat sebelumnya di antarmuka
for message in st.session_state.chat_history:
    role = "user" if message["role"] == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(message["parts"][0])

# Tangani input dari pengguna
if prompt := st.chat_input("Apa yang ingin Anda tanyakan?"):
    # Tampilkan input pengguna di antarmuka
    with st.chat_message("user"):
        st.markdown(prompt)

    # Kirim pesan ke model dan dapatkan respons
    try:
        response = st.session_state.chat_session.send_message(prompt, stream=True)
        
        # Tampilkan respons model di antarmuka secara bertahap
        with st.chat_message("assistant"):
            full_response = ""
            message_placeholder = st.empty()
            for chunk in response:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        
        # Tambahkan respons ke riwayat chat
        st.session_state.chat_history.append({"role": "user", "parts": [prompt]})
        st.session_state.chat_history.append({"role": "model", "parts": [full_response]})

    except Exception as e:
        st.error(f"Maaf, terjadi kesalahan saat berkomunikasi dengan Gemini: {e}")
        st.session_state.chat_history.append({"role": "user", "parts": [prompt]})
        st.session_state.chat_history.append({"role": "model", "parts": ["Maaf, saya tidak bisa memberikan balasan saat ini."]})
