import random
import time


def candidatos(tablero, fila, col):
    usados = set(tablero[fila])
    usados |= {tablero[r][col] for r in range(9)}
    f0, c0 = 3 * (fila // 3), 3 * (col // 3)
    usados |= {tablero[r][c] for r in range(f0, f0 + 3)
                              for c in range(c0, c0 + 3)}
    return [n for n in range(1, 10) if n not in usados]


def celda_mrv(tablero):
    """Devuelve (celda, candidatos) con menos opciones, o (None, None) si está completo."""
    mejor, mejores = None, None
    for f in range(9):
        for c in range(9):
            if tablero[f][c] == 0:
                cands = candidatos(tablero, f, c)
                if mejores is None or len(cands) < len(mejores):
                    mejor, mejores = (f, c), cands
                    if not cands:
                        return mejor, mejores
    return mejor, mejores


def resolver(tablero, aleatorio=False):
    """Backtracking + MRV. Con aleatorio=True baraja los candidatos (para generar)."""
    celda, cands = celda_mrv(tablero)
    if celda is None:
        return True
    if aleatorio:
        random.shuffle(cands)
    f, c = celda
    for n in cands:
        tablero[f][c] = n
        if resolver(tablero, aleatorio):
            return True
        tablero[f][c] = 0
    return False


def contar_soluciones(tablero, limite=2):
    """Cuenta soluciones (se detiene en 'limite') para garantizar unicidad."""
    celda, cands = celda_mrv(tablero)
    if celda is None:
        return 1
    f, c = celda
    total = 0
    for n in cands:
        tablero[f][c] = n
        total += contar_soluciones(tablero, limite - total)
        tablero[f][c] = 0
        if total >= limite:
            break
    return total


def generar_puzzle(vacias):
    """Genera (puzzle, solucion) con solución única."""
    solucion = [[0] * 9 for _ in range(9)]
    resolver(solucion, aleatorio=True)
    puzzle = [fila[:] for fila in solucion]

    posiciones = [(f, c) for f in range(9) for c in range(9)]
    random.shuffle(posiciones)
    quitadas = 0
    for f, c in posiciones:
        if quitadas >= vacias:
            break
        respaldo = puzzle[f][c]
        puzzle[f][c] = 0
        copia = [fila[:] for fila in puzzle]
        if contar_soluciones(copia) == 1:
            quitadas += 1
        else:
            puzzle[f][c] = respaldo
    return puzzle, solucion


def imprimir(tablero, fijas):
    print("\n     1 2 3   4 5 6   7 8 9")
    print("   +-------+-------+-------+")
    for f in range(9):
        partes = []
        for j in range(0, 9, 3):
            partes.append(" ".join(
                str(tablero[f][c]) if tablero[f][c] else "."
                for c in range(j, j + 3)))
        print(f" {f + 1} | " + " | ".join(partes) + " |")
        if f % 3 == 2:
            print("   +-------+-------+-------+")
    print()


AYUDA = """Comandos:
  F C N      poner el número N en fila F, columna C   (ej: 3 5 7)
  borrar F C vaciar una celda que tú llenaste         (ej: borrar 3 5)
  pista      el programa llena una celda por ti
  revisar    marca los errores que llevas
  resolver   muestra la solución (resuelta con backtracking + MRV)
  ayuda      muestra este mensaje
  salir      terminar
"""


def jugar():
    print("=== SUDOKU ===")
    niveles = {"1": ("Fácil", 36), "2": ("Medio", 46), "3": ("Difícil", 52)}
    while True:
        op = input("Dificultad (1=Fácil, 2=Medio, 3=Difícil): ").strip()
        if op in niveles:
            break
    nombre, vacias = niveles[op]

    print(f"\nGenerando Sudoku {nombre}...")
    puzzle, solucion = generar_puzzle(vacias)
    fijas = {(f, c) for f in range(9) for c in range(9) if puzzle[f][c]}
    tablero = [fila[:] for fila in puzzle]
    inicio = time.time()

    print(AYUDA)
    while True:
        imprimir(tablero, fijas)
        if tablero == solucion:
            seg = int(time.time() - inicio)
            print(f"¡Felicidades, lo resolviste en {seg // 60} min {seg % 60} s!")
            return

        partes = input("> ").strip().lower().split()
        if not partes:
            continue
        cmd = partes[0]

        if cmd == "salir":
            return
        elif cmd == "ayuda":
            print(AYUDA)
        elif cmd == "resolver":
            imprimir(solucion, fijas)
            print("Solución mostrada.")
            return
        elif cmd == "pista":
            vacias_ = [(f, c) for f in range(9) for c in range(9)
                       if tablero[f][c] != solucion[f][c]]
            f, c = random.choice(vacias_)
            tablero[f][c] = solucion[f][c]
            fijas.add((f, c))
            print(f"Pista: fila {f + 1}, columna {c + 1} = {solucion[f][c]}")
        elif cmd == "revisar":
            malas = [(f + 1, c + 1) for f in range(9) for c in range(9)
                     if tablero[f][c] and tablero[f][c] != solucion[f][c]]
            print("Errores en (fila, col):", malas if malas else "ninguno, vas bien")
        elif cmd == "borrar" and len(partes) == 3:
            try:
                f, c = int(partes[1]) - 1, int(partes[2]) - 1
                if not (0 <= f < 9 and 0 <= c < 9):
                    raise ValueError
            except ValueError:
                print("Fila y columna deben estar entre 1 y 9.")
                continue
            if (f, c) in fijas:
                print("Esa celda es una pista fija.")
            else:
                tablero[f][c] = 0
        elif len(partes) == 3 and all(p.isdigit() for p in partes):
            f, c, n = int(partes[0]) - 1, int(partes[1]) - 1, int(partes[2])
            if not (0 <= f < 9 and 0 <= c < 9 and 1 <= n <= 9):
                print("Fila, columna y número deben estar entre 1 y 9.")
            elif (f, c) in fijas:
                print("Esa celda es una pista fija.")
            else:
                tablero[f][c] = n
        else:
            print("Comando no reconocido. Escribe 'ayuda'.")


if __name__ == "__main__":
    jugar()