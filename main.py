import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import hashlib

# 設定頁面
st.set_page_config(
    page_title="店鋪庫存管理系統",
    page_icon="🏪",
    layout="wide"
)

# 自定義CSS樣式
st.markdown("""
    <style>
    .main {
        padding: 20px;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# 初始化資料庫
def init_db():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    return conn

# 主程式
def main():
    st.title("🏪 店鋪庫存管理系統")
    
    # 初始化 session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    # 登入/註冊介面
    if not st.session_state.logged_in:
        tab1, tab2 = st.tabs(["登入", "註冊"])
        
        # 登入頁面
        with tab1:
            username = st.text_input("帳號")
            password = st.text_input("密碼", type="password")
            if st.button("登入"):
                conn = init_db()
                c = conn.cursor()
                hashed_pwd = hashlib.sha256(password.encode()).hexdigest()
                c.execute("SELECT role FROM users WHERE username=? AND password=?", 
                         (username, hashed_pwd))
                result = c.fetchone()
                conn.close()
                
                if result:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("登入成功！")
                    st.rerun()
                else:
                    st.error("帳號或密碼錯誤")
        
        # 註冊頁面
        with tab2:
            new_username = st.text_input("新帳號")
            new_password = st.text_input("新密碼", type="password")
            confirm_password = st.text_input("確認密碼", type="password")
            invitation_code = st.text_input("邀請碼")
            
            if st.button("註冊"):
                if invitation_code != "love139674":
                    st.error("邀請碼錯誤")
                elif new_password != confirm_password:
                    st.error("密碼不一致")
                else:
                    conn = init_db()
                    try:
                        c = conn.cursor()
                        hashed_pwd = hashlib.sha256(new_password.encode()).hexdigest()
                        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                                (new_username, hashed_pwd, "管理員"))
                        conn.commit()
                        st.success("註冊成功！請返回登入頁面")
                    except sqlite3.IntegrityError:
                        st.error("此帳號已存在")
                    finally:
                        conn.close()
    
    # 主要功能介面
    else:
        st.write(f"歡迎, {st.session_state.username}!")
        
        if st.button("登出"):
            st.session_state.logged_in = False
            st.rerun()
        
        # 新增商品
        st.header("新增商品")
        col1, col2, col3 = st.columns(3)
        with col1:
            product_name = st.text_input("商品名稱")
        with col2:
            quantity = st.number_input("數量", min_value=0)
        with col3:
            price = st.number_input("單價", min_value=0.0)
        
        if st.button("新增"):
            conn = init_db()
            c = conn.cursor()
            c.execute("""
            INSERT INTO inventory (product_name, quantity, price, last_updated)
            VALUES (?, ?, ?, ?)
            """, (product_name, quantity, price, datetime.now()))
            conn.commit()
            conn.close()
            st.success("商品新增成功！")
        
        # 顯示庫存
        st.header("庫存列表")
        conn = init_db()
        df = pd.read_sql_query("SELECT * FROM inventory", conn)
        conn.close()
        
        if not df.empty:
            st.dataframe(df)
        else:
            st.info("目前沒有庫存記錄")

if __name__ == "__main__":
    main()
