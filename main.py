import streamlit as st
import pandas as pd
from datetime import datetime
import hashlib
import httpx
import os
from dotenv import load_dotenv
import json

# 載入環境變數
load_dotenv()

# Supabase API 設定
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

# Supabase API 函數
def supabase_query(table, method="GET", data=None, query_params=None):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    
    # 修改 headers，加入 Range
    headers = HEADERS.copy()
    headers["Range"] = "0-9"
    
    # Debug: 顯示請求資訊
    st.write("Debug: URL", url)
    st.write("Debug: Headers", headers)
    st.write("Debug: Query Params", query_params)
    
    try:
        with httpx.Client() as client:
            if method == "GET":
                if query_params:
                    # 構建查詢字串
                    filters = []
                    for key, value in query_params.items():
                        filters.append(f"{key}={value}")
                    query_string = "&".join(filters)
                    url = f"{url}?{query_string}"
                    st.write("Debug: Final URL", url)
                
                response = client.get(url, headers=headers)
                # Debug: 顯示回應資訊
                st.write("Debug: Response Status", response.status_code)
                st.write("Debug: Response Text", response.text)
            elif method == "POST":
                response = client.post(url, headers=headers, json=data)
            
            return response.json() if response.text else []
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return []

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
                hashed_pwd = hashlib.sha256(password.encode()).hexdigest()
                
                # Debug: 顯示加密後的密碼
                st.write("Debug: Hashed Password", hashed_pwd)
                
                # 直接使用 httpx 發送請求
                url = f"{SUPABASE_URL}/rest/v1/users"
                headers = HEADERS.copy()
                headers["Range"] = "0-9"
                
                # 構建查詢參數
                params = {
                    "select": "*",
                    "username": f"eq.{username}",
                    "password": f"eq.{hashed_pwd}"
                }
                
                # Debug
                st.write("Debug: Final URL", url)
                st.write("Debug: Params", params)
                
                try:
                    with httpx.Client() as client:
                        response = client.get(url, headers=headers, params=params)
                        st.write("Debug: Response Status", response.status_code)
                        st.write("Debug: Response Text", response.text)
                        
                        result = response.json() if response.text else []
                        
                        if result:
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            st.success("登入成功！")
                            st.rerun()
                        else:
                            st.error("帳號或密碼錯誤")
                except Exception as e:
                    st.error(f"登入錯誤：{str(e)}")
        
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
                    hashed_pwd = hashlib.sha256(new_password.encode()).hexdigest()
                    try:
                        # 新增使用者
                        data = {
                            "username": new_username,
                            "password": hashed_pwd,
                            "role": "管理員"
                        }
                        supabase_query('users', method="POST", data=data)
                        st.success("註冊成功！請返回登入頁面")
                    except Exception as e:
                        st.error("此帳號已存在")
    
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
            try:
                # 新增商品
                data = {
                    "product_name": product_name,
                    "quantity": quantity,
                    "price": price,
                    "last_updated": datetime.now().isoformat()
                }
                supabase_query('inventory', method="POST", data=data)
                st.success("商品新增成功！")
            except Exception as e:
                st.error(f"新增失敗：{str(e)}")
        
        # 顯示庫存
        st.header("庫存列表")
        try:
            # 讀取庫存
            result = supabase_query('inventory', method="GET")
            
            if result:
                df = pd.DataFrame(result)
                # 計算總金額
                df['總金額'] = df['quantity'] * df['price']
                
                # 顯示完整庫存列表
                st.subheader("完整庫存列表")
                st.dataframe(df)
                
                # 顯示品項統計
                st.subheader("品項統計")
                summary = df.groupby('product_name').agg({
                    'quantity': 'sum',
                    'price': 'first',  # 顯示單價
                    '總金額': 'sum'
                }).reset_index()
                summary.columns = ['商品名稱', '總數量', '單價', '總金額']
                st.dataframe(summary)
                
                # 顯示總計
                st.subheader("總計")
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"所有商品總數量：{summary['總數量'].sum():,.0f}")
                with col2:
                    st.info(f"所有商品總金額：${summary['總金額'].sum():,.2f}")
            else:
                st.info("目前沒有庫存記錄")
        except Exception as e:
            st.error(f"讀取失敗：{str(e)}")

if __name__ == "__main__":
    main()
