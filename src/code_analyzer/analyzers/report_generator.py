from typing import Any, Dict
import json
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

class ReportGenerator:
    def __init__(self, output_format: str = 'console'):
        self.output_format = output_format
        self.console = Console()

    def generate(self, results: Dict[str, Any]) -> None:
        if self.output_format == 'console':
            self._to_console(results)
        elif self.output_format == 'json':
            print(json.dumps(results, indent=2, ensure_ascii=False))
        elif self.output_format == 'html':
            self._to_html(results)

    def _to_console(self, results: Dict[str, Any]) -> None:
        console = self.console
        # Banner
        banner = Text("anatooly", justify="center", style="bold magenta")
        subtitle = Text("Security Code Analyzer", justify="center", style="bold green")
        console.print(Panel(banner + "\n" + subtitle, expand=False, box=box.DOUBLE))

        # Language Distribution
        langs = results.get('languages', {})
        table_lang = Table(title="Language Distribution", box=box.SIMPLE_HEAVY)
        table_lang.add_column("Language", style="cyan bold")
        table_lang.add_column("%", style="white bold", justify="right")
        for lang, perc in sorted(langs.items(), key=lambda x: -x[1]):
            table_lang.add_row(lang, f"{perc:.2f}%")
        console.print(table_lang)

        # SLOC
        sloc = results.get('sloc', {})
        by_lang = sloc.get('by_lang', {})
        total = sloc.get('total', 0)
        table_sloc = Table(title=f"Source Lines of Code: {total}", box=box.SIMPLE_HEAVY)
        table_sloc.add_column("Language", style="cyan")
        table_sloc.add_column("Lines", style="white", justify="right")
        for lang, count in sorted(by_lang.items(), key=lambda x: -x[1]):
            table_sloc.add_row(lang, str(count))
        console.print(table_sloc)

        # Technology Stack
        stack = results.get('stack', {}) or {}
        panels = []
        for category, techs in stack.items():
            if techs:
                tech_list = "\n".join(f"- {t}" for t in sorted(techs))
                panels.append(Panel(tech_list, title=category.capitalize(), box=box.ROUNDED))
        if panels:
            console.print(Panel(Text("Technology Stack", style="bold underline"), box=box.SIMPLE))
            for p in panels:
                console.print(p)

        # Endpoints
        eps = results.get('endpoints', [])
        if eps:
            table_ep = Table(title="API Endpoints", box=box.SIMPLE_HEAVY)
            table_ep.add_column("File", style="magenta")
            table_ep.add_column("Line", style="green", justify="right")
            table_ep.add_column("Method", style="yellow")
            table_ep.add_column("Framework", style="cyan")
            table_ep.add_column("Route", style="white")
            for ep in eps:
                table_ep.add_row(
                    ep['file'], str(ep['line']), ep['method'], ep['framework'], ep['endpoint']
                )
            console.print(table_ep)
        else:
            console.print(Panel("No API endpoints found", style="red"))

        # AJAX
        ajax = results.get('ajax', [])
        if ajax:
            table_ajax = Table(title="AJAX Calls", box=box.SIMPLE_HEAVY)
            table_ajax.add_column("File", style="magenta")
            table_ajax.add_column("Line", style="green", justify="right")
            table_ajax.add_column("Call", style="white")
            for call in ajax:
                table_ajax.add_row(call['file'], str(call['line']), call['call'])
            console.print(table_ajax)
        else:
            console.print(Panel("No AJAX calls found", style="red"))

        # HTTP Methods
        http_methods = results.get('http_methods', [])
        if http_methods:
            table_m = Table(title="HTTP Methods", box=box.SIMPLE_HEAVY)
            table_m.add_column("File", style="magenta")
            table_m.add_column("Line", style="green", justify="right")
            table_m.add_column("Method", style="yellow")
            table_m.add_column("Context", style="white")
            for m in http_methods:
                table_m.add_row(m['file'], str(m['line']), m['method'], m.get('context',''))
            console.print(table_m)
        else:
            console.print(Panel("No HTTP methods found", style="red"))

        # HTTP Headers
        table_h = Table(show_header=True, header_style="bold cyan")
        table_h.add_column("File", overflow="fold")
        table_h.add_column("Line", justify="right")
        table_h.add_column("Header")
        table_h.add_column("Value", overflow="fold")

        headers = results.get("headers", [])
        if headers:
            for h in headers:
                hdr_dict = h["headers"]
                hdr_text = json.dumps(hdr_dict, ensure_ascii=False)
                value = h.get("value")
                val_text = "" if value is None else str(value)

                table_h.add_row(
                    h["file"],
                    str(h["line"]),
                    hdr_text,
                    val_text
                )
            console.print(table_h)
        else:
            console.print(Panel("No HTTP headers found", style="dim"))

    def _to_html(self, results: Dict[str, Any]) -> None:

        html_parts = []
        html_parts.append('<!DOCTYPE html>')
        html_parts.append('<html lang="ru">')
        html_parts.append('<head>')
        html_parts.append('  <meta charset="utf-8" />')
        html_parts.append('  <title>Security Code Analysis Report</title>')
        html_parts.append('  <style>')
        html_parts.append('    body { font-family: Arial, sans-serif; padding: 20px; }')
        html_parts.append('    h1, h2, h3 { color: #333; }')
        html_parts.append('    table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }')
        html_parts.append('    th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }')
        html_parts.append('    th { background-color: #f5f5f5; }')
        html_parts.append('  </style>')
        html_parts.append('</head>')
        html_parts.append('<body>')
        html_parts.append('<h1>Security Code Analysis Report</h1>')

        # Языки
        html_parts.append('<h2>Language Distribution</h2>')
        html_parts.append('<table>')
        html_parts.append('<tr><th>Language</th><th>Percentage</th></tr>')
        for lang, perc in results.get('languages', {}).items():
            html_parts.append(f'<tr><td>{lang}</td><td>{perc:.2f}%</td></tr>')
        html_parts.append('</table>')

        # SLOC
        sloc = results.get('sloc', {})
        html_parts.append(f'<h2>SLOC: total {sloc.get("total", 0)}</h2>')
        html_parts.append('<table>')
        html_parts.append('<tr><th>Language</th><th>Lines</th></tr>')
        for lang, count in sloc.get('by_lang', {}).items():
            html_parts.append(f'<tr><td>{lang}</td><td>{count}</td></tr>')
        html_parts.append('</table>')

        # Технологический стек
        html_parts.append('<h2>Technology Stack</h2>')
        for category, techs in results.get('stack', {}).items():
            if techs:
                html_parts.append(f'<h3>{category.capitalize()}</h3>')
                html_parts.append('<ul>')
                for tech in sorted(techs):
                    html_parts.append(f'<li>{tech}</li>')
                html_parts.append('</ul>')

        # Dependencies
        html_parts.append('<h2>Dependencies</h2>')
        html_parts.append('<ul>')
        for cat, items in results.get('dependencies', {}).items():
            html_parts.append(f'<li>{cat}: {", ".join(sorted(items))}</li>')
        html_parts.append('</ul>')

        # Secrets
        secrets = results.get('secrets', [])
        if secrets:
            html_parts.append('<h2>Potential Secrets</h2>')
            for path, items in secrets:
                html_parts.append(f'<h3>{path}</h3>')
                html_parts.append('<ul>')
                for val in items:
                    html_parts.append(f'<li>{val}</li>')
                html_parts.append('</ul>')

        # Endpoints
        endpoints = results.get('endpoints', [])
        html_parts.append('<h2>API Endpoints</h2>')
        html_parts.append('<table>')
        html_parts.append('<tr><th>File</th><th>Line</th><th>Method</th><th>Framework</th><th>Route</th></tr>')
        for ep in endpoints:
            html_parts.append(
                f'<tr><td>{ep["file"]}</td><td>{ep["line"]}</td><td>{ep["method"]}</td>'
                f'<td>{ep["framework"]}</td><td>{ep["endpoint"]}</td></tr>'
            )
        html_parts.append('</table>')

        # AJAX Calls
        ajax = results.get('ajax', [])
        html_parts.append('<h2>AJAX Calls</h2>')
        html_parts.append('<table>')
        html_parts.append('<tr><th>File</th><th>Line</th><th>Call</th></tr>')
        for call in ajax:
            html_parts.append(f'<tr><td>{call["file"]}</td><td>{call["line"]}</td><td>{call["call"]}</td></tr>')
        html_parts.append('</table>')

        html_parts.append('</body>')
        html_parts.append('</html>')

        # Write to file
        output_path = os.path.join(os.getcwd(), 'report.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(html_parts))
        print(f"HTML report generated: {output_path}")
