from flask import Flask, render_template, request, jsonify
import ply.lex as lex
import ply.yacc as yacc

app = Flask(__name__)

tokens = ('NUMBER', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'LPAREN', 'RPAREN')

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'

t_ignore = ' \t'

def t_NUMBER(t):
    r'\d+(\.\d+)?'
    t.value = float(t.value) if '.' in t.value else int(t.value)
    return t

def t_error(t):
    print("Caracter no reconocido: '%s'" % t.value[0])
    t.lexer.skip(1)

lexer = lex.lex()

def p_expression_binop(p):
    '''expression : expression PLUS term
                  | expression MINUS term'''
    p[0] = ('op', p[2], p[1], p[3])

def p_expression_term(p):
    'expression : term'
    p[0] = p[1]

def p_term_binop(p):
    '''term : term TIMES factor
            | term DIVIDE factor'''
    p[0] = ('op', p[2], p[1], p[3])

def p_term_factor(p):
    'term : factor'
    p[0] = p[1]

def p_factor_num(p):
    'factor : NUMBER'
    p[0] = ('num', p[1])

def p_factor_expr(p):
    'factor : LPAREN expression RPAREN'
    p[0] = p[2]

def p_error(p):
    print("Error de sintaxis")

parser = yacc.yacc()

def format_expression(expression):
    expression = expression.replace(')(', ')*(')
    
    processed = ""
    i = 0
    while i < len(expression):
        if i > 0 and expression[i] == '(' and (expression[i - 1].isdigit() or expression[i - 1] == ')'):
            processed += '*('
        else:
            processed += expression[i]
        i += 1
    return processed

@app.route('/')
def calculadora():
    return render_template('index.html')


@app.route('/analizar', methods=['POST'])
def analizar_expresion():
    try:
        data = request.get_json()
        input_expr = data.get('input')

        if not input_expr:
            return jsonify({"error": "No se recibió ninguna expresión"}), 400

        formatted_expr = format_expression(input_expr)
        resultado = parser.parse(formatted_expr)

        return jsonify({"arbol": resultado})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/calcular', methods=['POST'])
def calcular_expresion():
    try:
        data = request.get_json()
        input_expr = data.get('input')
        
        if not input_expr:
            return jsonify({"error": "No se recibió ninguna expresión"}), 400
        
        formatted_expr = format_expression(input_expr)
        
        resultado = eval(formatted_expr)
        
        return jsonify({"resultado": resultado})
    except Exception as e:
        return jsonify({"error": "Error en la evaluación de la expresión"}), 500

if __name__ == '__main__':
    app.run(debug=True)
