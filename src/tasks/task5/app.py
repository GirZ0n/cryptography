import streamlit as st

from src.tasks.task5.md5 import MD5

if __name__ == '__main__':
    st.set_page_config(page_title='MD5')

    st.title('MD5 Hash Generator')

    text = st.text_area('Text')

    int_hash = MD5.hash(text)
    hex_hash = hex(int_hash)[2:].zfill(32)

    st.subheader('Hash:')
    st.text(hex_hash)
