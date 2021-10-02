import re
import sys

import streamlit as st
from bitarray.util import ba2hex, hex2ba

sys.path.append('')
sys.path.append('../../..')

from src.tasks.task2.main import decode, encode


def show_encoder():
    text = st.text_input('Text:')
    key = st.text_input('Key:', max_chars=14, key='encoder_key')

    if key != '' and not re.match('^[0-9a-fA-F]+$', key):
        st.error('Key must be in hexadecimal.')

    if text != '' and key != '' and not re.match('^[0-9a-fA-F]+$', key):
        encrypted_text = encode(text, key)
        st.markdown('**Encrypted text**')
        st.markdown(ba2hex(encrypted_text))

    return key


def show_decoder(key: str):
    encrypted_text = st.text_input('Encrypted text:')
    key = st.text_input('Key:', max_chars=14, value=key, key='decoder_key')

    if encrypted_text != '' and not re.match('^[0-9a-fA-F]+$', encrypted_text):
        st.error('Text must be in hexadecimal.')
        st.stop()

    if key != '' and not re.match('^[0-9a-fA-F]+$', key):
        st.error('Key must be in hexadecimal.')
        st.stop()

    if encrypted_text != '' and key != '':
        decrypted_text = decode(hex2ba(encrypted_text), key)
        st.markdown('**Decrypted text**')
        try:
            st.markdown(decrypted_text.tobytes().decode().strip('\x00'))
        except UnicodeDecodeError:
            st.markdown(ba2hex(decrypted_text))


def main():
    st.header('Data Encryption Standard (DES)')

    left_column, right_column = st.columns(2)
    with left_column:
        st.subheader('Encoder')
        key = show_encoder()

    with right_column:
        st.subheader('Decoder')
        show_decoder(key)


if __name__ == '__main__':
    st.set_page_config(page_title='DES', layout='wide')
    main()
