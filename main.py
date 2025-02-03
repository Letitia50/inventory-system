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
    "Content-Type": "application/json"
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
    st.title("登入測試")
    
    username = st.text_input("帳號")
    password = st.text_input("密碼", type="password")
    
    if st.button("登入"):
        hashed_pwd = hashlib.sha256(password.encode()).hexdigest()
        
        # Debug
        st.write("Debug: 輸入資訊", {
            "username": username,
            "hashed_password": hashed_pwd
        })
        
        try:
            url = f"{SUPABASE_URL}/rest/v1/users"
            params = {
                "username": f"eq.{username}",
                "password": f"eq.{hashed_pwd}"
            }
            
            # Debug
            st.write("Debug: 請求 URL", url)
            st.write("Debug: 請求參數", params)
            
            with httpx.Client() as client:
                response = client.get(url, headers=HEADERS, params=params)
                
                # Debug
                st.write("Debug: 完整 URL", response.url)
                st.write("Debug: 狀態碼", response.status_code)
                st.write("Debug: 回應內容", response.text)
                
                if response.status_code == 200:
                    result = response.json()
                    if result:
                        st.success("登入成功！")
                        st.write("用戶資料：", result)
                    else:
                        st.error("帳號或密碼錯誤")
                else:
                    st.error(f"API 錯誤：{response.status_code}")
                    
        except Exception as e:
            st.error(f"錯誤：{str(e)}")

if __name__ == "__main__":
    main()
