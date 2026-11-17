#!/usr/bin/env python3
# Regenera emplac.json (rows do mapa) a partir de ../emplacamentos_detalhe_2026.csv.
# Mantem as MESMAS listas fabs/fams ja existentes em emplac.json (universo curado:
# so familias que a Guerra fabrica, decisao 2026-10-02) - nao adiciona fabricante/familia novo,
# so filtra linhas que nao casam (ficam fora do escopo, nao e erro).
# Mesmas exclusoes de negocio do cenario oficial: Bachiega, Bendo Alimentos, Canavieiro, Usina Acucareira.
import csv, json, unicodedata, re

def norm(s):
    s = unicodedata.normalize('NFD', str(s))
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = s.upper().replace('.', ' ')
    return re.sub(r'\s+', ' ', s).strip()

def excluido(cliente, segmento):
    c = cliente.upper()
    if 'BACHIEGA' in c: return True
    if 'BENDO ALIMENTOS' in c: return True
    if segmento.strip().upper() == 'CANAVIEIRO': return True
    if 'USINA ACUCAREIRA' in c or 'USINA AÇUCAREIRA' in c: return True
    return False

old = json.load(open('emplac.json'))
fabs, fams = old['fabs'], old['fams']
fab_idx = {norm(f): i for i, f in enumerate(fabs)}
fam_idx = {norm(f): i for i, f in enumerate(fams)}
reg = json.load(open('data.json'))
reg_keys = set(reg.keys())

rows = []
with open('../emplacamentos_detalhe_2026.csv', encoding='utf-8-sig') as f:
    for row in csv.DictReader(f, delimiter=';'):
        cli, seg = row['Cliente'].strip(), row['Familia_Produto'].strip()
        fab, cidade = row['Fabricante'].strip(), row['Municipio'].strip()
        qtd = int(row['Emplacamentos'])
        if excluido(cli, seg):
            continue
        fi, mi, ck = fab_idx.get(norm(fab)), fam_idx.get(norm(seg)), norm(cidade)
        if fi is None or mi is None or ck not in reg_keys:
            continue
        marca = 0 if fabs[fi] == 'GUERRA' else 1
        rows.append([ck, fi, mi, marca, qtd])

json.dump({'fabs': fabs, 'fams': fams, 'rows': rows}, open('emplac.json', 'w'), ensure_ascii=False, separators=(',', ':'))
tot = sum(r[4] for r in rows); g = sum(r[4] for r in rows if r[3] == 0)
print('rows:', len(rows), '| total:', tot, '| Guerra:', g, f'({100*g/tot:.1f}%)' if tot else '')
