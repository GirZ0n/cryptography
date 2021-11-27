import streamlit as st
import sympy

_PRIME_NUMBER_LEFT_BOUNDARY = 1000
_PRIME_NUMBER_RIGHT_BOUNDARY = 1000000


def get_power_over_modulus(number: int, power: int, modulus: int) -> int:
    answer = 1
    for _ in range(power):
        answer = answer * number % modulus
    return answer


def main():
    st.title('Протокол Диффи — Хеллмана')

    st.session_state.setdefault('p', 23)
    st.session_state.setdefault('g', 5)

    left_column, right_column = st.columns(2)

    with left_column:
        p = int(st.number_input('p:', help='Случайное простое число', value=st.session_state.get('p')))

    with right_column:
        g = int(st.number_input('g:', help=f'Случайное простое число', value=st.session_state.get('g')))

    if st.button('Сгенерировать p и g'):
        st.session_state['p'] = sympy.ntheory.randprime(_PRIME_NUMBER_LEFT_BOUNDARY, _PRIME_NUMBER_RIGHT_BOUNDARY)
        st.session_state['g'] = sympy.ntheory.randprime(_PRIME_NUMBER_LEFT_BOUNDARY, _PRIME_NUMBER_RIGHT_BOUNDARY)
        st.experimental_rerun()

    left_column, right_column = st.columns(2)

    st.session_state.setdefault('a', -1)
    st.session_state.setdefault('b', -1)

    with left_column:
        st.header('Алиса')

        a = int(st.number_input('Cекретный ключ Алисы:', value=st.session_state['a']))
        if a != -1:
            st.session_state['a'] = a

            A = get_power_over_modulus(g, a, p)
            st.markdown(fr'Открытый ключ Алисы: $A = g^a \ (mod \ p) = {g}^{{{a}}}\ (mod\ {p}) = {A}$')

            B = int(st.number_input('Открытый ключ Боба:', value=-1))
            if B != -1:
                K = get_power_over_modulus(B, a, p)
                st.markdown(fr'Секретный ключ: $K = B^a \ (mod \ p) = {B}^{{{a}}} \ (mod \ {p}) = {K}$')

    with right_column:
        st.header('Боб')

        b = int(st.number_input('Cекретный ключ Боба:', value=st.session_state['b']))
        if b != -1:
            st.session_state['b'] = b

            B = get_power_over_modulus(g, b, p)
            st.markdown(fr'Открытый ключ Боба: $B = g^b \ (mod \ p) = {g}^{{{b}}}\ (mod\ {p}) = {B}$')

            A = int(st.number_input('Открытый ключ Алисы:', value=-1))
            if A != -1:
                K = get_power_over_modulus(A, b, p)
                st.markdown(fr'Секретный ключ: $K = A^b \ (mod \ p) = {A}^{{{b}}} \ (mod \ {p}) = {K}$')


if __name__ == '__main__':
    st.set_page_config(layout='wide', page_title='DH')
    main()
