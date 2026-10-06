import os
import streamlit as st
from google import genai
from google.genai import types

# ページ基本設定
st.set_page_config(
    page_title="LeanBulk AI Pro",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# タイトル
st.title("💪 LeanBulk AI Pro")
st.caption("あなた専用のパーソナル食事・トレーニング・ボディチェック管理アプリ")

# APIキーの取得（環境変数から）
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️️ GEMINI_API_KEY が設定されていません。StreamlitのSecrets設定でAPIキーを登録してください。")
    st.stop()

# Geminiクライアントの初期化
client = genai.Client(api_key=api_key)

# タブ切り替え
tab1, tab2, tab3 = st.tabs(["📸 AI食事・カロリー計算", "🏋️‍♂️ PPLトレログ", "📸 AIボディチェック"])

# --- TAB 1: AI食事・カロリー計算 ---
with tab1:
    st.header("📸 食事解析 & PFC自動計算")
    st.info("夜勤/日勤シフトに合わせたPFCバランスを自動チェックします。脂質は40g以下を意識！")
    
    input_type = st.radio("入力方法を選択", ["テキスト入力", "画像アップロード"], horizontal=True)
    
    prompt_text = ""
    image_bytes = None
    
    if input_type == "テキスト入力":
        user_text = st.text_area("食べたものを入力（例: 鯖缶1缶、白米200g、味噌汁、納豆1パック）")
        if user_text:
            prompt_text = f"以下の食事のカロリーおよびPFC（タンパク質・脂質・炭水化物）を概算し、リーンバルク（脂質抑えめ・高タンパク）の観点から簡潔にアドバイスしてください:\n{user_text}"
            
    else:
        uploaded_file = st.file_uploader("食事の写真をアップロード", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            image_bytes = uploaded_file.read()
            st.image(image_bytes, caption="アップロードされた食事画像", use_column_width=True)
            prompt_text = "この画像に写っている食事のカロリーおよびPFC（タンパク質・脂質・炭水化物）を推定し、リーンバルク視点でのワンポイントアドバイスを簡潔に教えてください。"

    if st.button("AIで解析する", key="analyze_food"):
        if not prompt_text:
            st.warning("食事内容を入力するか、画像をアップロードしてください。")
        else:
            with st.spinner("AIが栄養素を解析中..."):
                try:
                    contents = []
                    if image_bytes:
                        contents.append(types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"))
                    contents.append(prompt_text)
                    
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=contents
                    )
                    st.success("解析完了！")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")

# --- TAB 2: PPLトレログ ---
with tab2:
    st.header("🏋️‍♂️ PPL トレーニング記録")
    workout_type = st.selectbox("本日のトレーニング種別", ["Push (胸・肩前中部・三頭)", "Pull (背中・肩後部・二頭)", "Legs (脚・腹筋)"])
    
    col1, col2 = st.columns(2)
    with col1:
        exercise = st.text_input("種目名", value="ベンチプレス")
        weight = st.number_input("重量 (kg)", value=80.0, step=2.5)
    with col2:
        reps = st.number_input("レップ数 (Rep)", value=8, step=1)
        sets = st.number_input("セット数", value=3, step=1)
        
    memo = st.text_area("意識ポイント・メモ", value="ボトムでしっかり受けて爆発的に押す。肘を引き寄せるイメージ。")
    
    if st.button("記録を保存する", key="save_workout"):
        st.success(f"【{workout_type}】{exercise} {weight}kg × {reps}レップ ({sets}セット) を記録しました！")

# --- TAB 3: AIボディチェック ---
with tab3:
    st.header("📸 トレ後ボディチェック & AI評価")
    st.info("トレ後の写真から、張り具合・むくみ・カットをAIが客観的に分析します！")
    
    body_file = st.file_uploader("身体の写真をアップロード", type=["jpg", "jpeg", "png"], key="body_img")
    
    if body_file is not None:
        body_bytes = body_file.read()
        st.image(body_bytes, caption="今日のコンディション", use_column_width=True)
        
        if st.button("AIコンディション評価を実行", key="analyze_body"):
            with st.spinner("筋肉の張り・カット・水分の抜け具合を解析中..."):
                try:
                    body_prompt = """
                    あなたはフィジーク大会を目指すトレーナーです。
                    アップロードされた写真の身体のコンディションをプロの視点から客観的に評価してください。
                    以下のポイントを含めてフィードバックしてください：
                    1. 筋肉の張り（パンプ感・ボリューム）
                    2. むくみ・皮下水分の抜け具合
                    3. 大胸筋・肩・腹筋等のカット・仕上がり評価
                    4. 次のトレーニングや食事に向けた一言アドバイス
                    """
                    
                    contents = [
                        types.Part.from_bytes(data=body_bytes, mime_type="image/jpeg"),
                        body_prompt
                    ]
                    
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=contents
                    )
                    st.success("評価完了！")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
