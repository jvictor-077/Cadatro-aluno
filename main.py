import sqlite3
from tkinter import *
from tkinter import ttk, messagebox
from reportlab.pdfgen import canvas

# Conecta ao banco
conn = sqlite3.connect("escola.db")
cursor = conn.cursor()

# Criação das tabelas
cursor.execute("""
CREATE TABLE IF NOT EXISTS alunos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT
);
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS disciplinas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT
);
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS notas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_id INTEGER,
    disciplina_id INTEGER,
    bimestre1 REAL,
    bimestre2 REAL,
    bimestre3 REAL,
    bimestre4 REAL,
    FOREIGN KEY(aluno_id) REFERENCES alunos(id),
    FOREIGN KEY(disciplina_id) REFERENCES disciplinas(id)
);
""")
conn.commit()

# Funções principais
def cadastrar_aluno():
    nome = entry_nome_aluno.get()
    if nome:
        cursor.execute("INSERT INTO alunos (nome) VALUES (?)", (nome,))
        conn.commit()
        messagebox.showinfo("Sucesso", "Aluno cadastrado!")
        entry_nome_aluno.delete(0, END)
        atualizar_alunos()

def cadastrar_disciplina():
    nome = entry_nome_disciplina.get()
    if nome:
        cursor.execute("INSERT INTO disciplinas (nome) VALUES (?)", (nome,))
        conn.commit()
        messagebox.showinfo("Sucesso", "Disciplina cadastrada!")
        entry_nome_disciplina.delete(0, END)
        atualizar_disciplinas()

def atualizar_alunos():
    alunos_cb['values'] = [f"{row[0]} - {row[1]}" for row in cursor.execute("SELECT * FROM alunos").fetchall()]

def atualizar_disciplinas():
    disciplinas_cb['values'] = [f"{row[0]} - {row[1]}" for row in cursor.execute("SELECT * FROM disciplinas").fetchall()]

def salvar_notas():
    try:
        aluno_id = int(alunos_cb.get().split(" - ")[0])
        disciplina_id = int(disciplinas_cb.get().split(" - ")[0])
        notas = [float(entry_b1.get()), float(entry_b2.get()), float(entry_b3.get()), float(entry_b4.get())]
        cursor.execute("""
            INSERT INTO notas (aluno_id, disciplina_id, bimestre1, bimestre2, bimestre3, bimestre4)
            VALUES (?, ?, ?, ?, ?, ?)""", (aluno_id, disciplina_id, *notas))
        conn.commit()
        messagebox.showinfo("Sucesso", "Notas salvas!")
    except Exception as e:
        messagebox.showerror("Erro", str(e))

def calcular_media():
    try:
        aluno_id = int(alunos_cb.get().split(" - ")[0])
        disciplina_id = int(disciplinas_cb.get().split(" - ")[0])
        nota = cursor.execute("""
            SELECT bimestre1, bimestre2, bimestre3, bimestre4
            FROM notas WHERE aluno_id=? AND disciplina_id=?
        """, (aluno_id, disciplina_id)).fetchone()
        if nota:
            media = sum(nota)/4
            situacao = "Aprovado" if media >= 6 else "Reprovado"
            messagebox.showinfo("Resultado", f"Média: {media:.2f}\nSituação: {situacao}")
            gerar_pdf(alunos_cb.get(), media, situacao)
        else:
            messagebox.showwarning("Aviso", "Notas não encontradas.")
    except Exception as e:
        messagebox.showerror("Erro", str(e))

def gerar_pdf(nome, media, situacao):
    nome_formatado = nome.replace(" ", "_")
    c = canvas.Canvas(f"{nome_formatado}_boletim.pdf")
    c.drawString(100, 750, f"Boletim Escolar - {nome}")
    c.drawString(100, 730, f"Média Final: {media:.2f}")
    c.drawString(100, 710, f"Situação: {situacao}")
    c.save()
    messagebox.showinfo("PDF", "Boletim gerado com sucesso!")

def mostrar_boletim():
    boletim_win = Toplevel(janela)
    boletim_win.title("Boletim Escolar")

    tree = ttk.Treeview(boletim_win, columns=("Aluno", "Disciplina", "B1", "B2", "B3", "B4", "Média", "Situação"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    tree.pack(fill=BOTH, expand=True)

    dados = cursor.execute("""
        SELECT a.nome, d.nome, n.bimestre1, n.bimestre2, n.bimestre3, n.bimestre4
        FROM notas n
        JOIN alunos a ON a.id = n.aluno_id
        JOIN disciplinas d ON d.id = n.disciplina_id
    """).fetchall()

    for aluno, disc, b1, b2, b3, b4 in dados:
        media = (b1 + b2 + b3 + b4) / 4
        situacao = "Aprovado" if media >= 6 else "Reprovado"
        tree.insert("", END, values=(aluno, disc, b1, b2, b3, b4, f"{media:.2f}", situacao))

# Interface Tkinter
janela = Tk()
janela.title("Sistema Escolar")
janela.geometry("500x600")

Label(janela, text="Nome do Aluno").pack()
entry_nome_aluno = Entry(janela)
entry_nome_aluno.pack()
Button(janela, text="Cadastrar Aluno", command=cadastrar_aluno).pack(pady=5)

Label(janela, text="Nome da Disciplina").pack()
entry_nome_disciplina = Entry(janela)
entry_nome_disciplina.pack()
Button(janela, text="Cadastrar Disciplina", command=cadastrar_disciplina).pack(pady=5)

Label(janela, text="Selecionar Aluno").pack()
alunos_cb = ttk.Combobox(janela)
alunos_cb.pack()
Label(janela, text="Selecionar Disciplina").pack()
disciplinas_cb = ttk.Combobox(janela)
disciplinas_cb.pack()

Label(janela, text="Notas Bimestrais").pack()
entry_b1 = Entry(janela); entry_b1.pack()
entry_b2 = Entry(janela); entry_b2.pack()
entry_b3 = Entry(janela); entry_b3.pack()
entry_b4 = Entry(janela); entry_b4.pack()

Button(janela, text="Salvar Notas", command=salvar_notas).pack(pady=5)
Button(janela, text="Calcular Média e Situação", command=calcular_media).pack(pady=5)
Button(janela, text="Mostrar Boletim Geral", command=mostrar_boletim).pack(pady=10)

atualizar_alunos()
atualizar_disciplinas()

janela.mainloop()
