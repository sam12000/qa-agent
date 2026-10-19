import json, pathlib, datetime
from jinja2 import Template
from .llm import ask

SYSTEM = """Tu es un testeur QA. À partir du test et du log d'échec, rédige une fiche
d'anomalie en JSON avec exactement ces clés :
titre, severite (Bloquante|Majeure|Mineure|Cosmétique), etapes (liste),
resultat_attendu, resultat_obtenu, hypothese.
N'invente aucun fait absent du log."""

HTML = Template("""<!doctype html><meta charset="utf-8">
<title>{{ r.titre }}</title>
<h1>{{ 'PASS' if passed else r.titre }}</h1>
<p><b>Date :</b> {{ date }} — <b>URL :</b> {{ url }} — <b>Tentatives :</b> {{ attempts }}</p>
{% if not passed %}
<p><b>Sévérité :</b> {{ r.severite }}</p>
<h2>Étapes de reproduction</h2><ol>{% for e in r.etapes %}<li>{{ e }}</li>{% endfor %}</ol>
<h2>Résultat attendu</h2><p>{{ r.resultat_attendu }}</p>
<h2>Résultat obtenu</h2><p>{{ r.resultat_obtenu }}</p>
<h2>Preuves</h2>{% for img in shots %}<img src="{{ img }}" width="700"><br>{% endfor %}
<p>Trace : <code>playwright show-trace {{ trace }}</code></p>
{% endif %}
<h2>Accessibilité ({{ a11y|length }} violations)</h2>
<ul>{% for v in a11y %}<li>[{{ v.impact }}] {{ v.description }} — {{ v.elements }} élément(s)</li>{% endfor %}</ul>
<h2>Test généré</h2><pre>{{ code }}</pre>""")

def build_report(result: dict, url: str, a11y: list[dict]) -> str:
    out = pathlib.Path(result["artifacts"]); out.mkdir(parents=True, exist_ok=True)
    fiche = {}
    if not result["passed"]:
        fiche = json.loads(ask(SYSTEM, f"Test :\n{result['code']}\n\nLog :\n{result['log'][-4000:]}",
                               json_mode=True))
    shots = [p.relative_to(out).as_posix() for p in out.rglob("*.png")]
    traces = list(out.rglob("trace.zip"))
    html = HTML.render(r=fiche, passed=result["passed"], url=url, a11y=a11y,
                       attempts=result["attempts"], code=result["code"], shots=shots,
                       trace=traces[0] if traces else "-",
                       date=datetime.datetime.now().strftime("%d/%m/%Y %H:%M"))
    (out / "fiche.json").write_text(json.dumps(fiche, ensure_ascii=False, indent=2), encoding="utf-8")
    path = out / "rapport.html"
    path.write_text(html, encoding="utf-8")
    return str(path)