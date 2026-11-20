# -*- coding: utf-8 -*-
"""Gemeinsame Vorgabe fuer alle Tests: das Hausdesign gilt, die Design-Sperre haelt nichts an.

master/core.py legt seine Farben und Schriften beim Import fest (master/design.py). Ohne Vorgabe wuerde ein Test an der Sperre
scheitern, solange die Werkstatt kein Design festgelegt hat - und die Pruefsummen in test_bausatz.py haengen am Hausdesign.
Darum steht die Umgebungsvariable schon beim Laden dieser Datei fest, vor dem ersten `import core`.
"""
import os

os.environ["REPORT_DESIGN"] = "haus"
