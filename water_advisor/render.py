import streamlit.components.v1 as components
import json

def render_grouped_bar_chart(data_by_label, labels, title):
    datasets = []
    colors = ["#007bff", "#28a745", "#ffc107", "#dc3545", "#6f42c1"]  # For resources
    for i, (resource, values) in enumerate(data_by_label.items()):
        datasets.append({
            "label": resource,
            "backgroundColor": colors[i % len(colors)],
            "data": values
        })

    chart_html = f"""
    <html>
    <head>
      <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
    <canvas id="barChart"></canvas>
    <script>
    new Chart(document.getElementById('barChart'), {{
        type: 'bar',
        data: {{
            labels: {json.dumps(labels)},
            datasets: {json.dumps(datasets)}
        }},
        options: {{
            responsive: true,
            plugins: {{
                title: {{
                    display: true,
                    text: '{title}'
                }}
            }},
            scales: {{
                x: {{ stacked: false }},
                y: {{ stacked: false, beginAtZero: true }}
            }}
        }}
    }});
    </script>
    </body>
    </html>
    """
    components.html(chart_html, height=500)

def render_single_bar_chart(data_points, labels, title):
    chart_html = f"""
    <html>
    <head>
      <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
      <canvas id="totalChart"></canvas>
      <script>
        const ctx = document.getElementById('totalChart').getContext('2d');
        new Chart(ctx, {{
          type: 'bar',
          data: {{
            labels: {json.dumps(labels)},
            datasets: [{{
              label: '{title}',
              data: {json.dumps(data_points)},
              backgroundColor: 'rgba(75, 192, 192, 0.6)'
            }}]
          }},
          options: {{
            responsive: true,
            scales: {{
                y: {{
                beginAtZero: true
              }}
            }}
          }}
        }});
      </script>
    </body>
    </html>
    """

    components.html(chart_html, height=450)
