<!DOCTYPE html>
<html>
<head>
    <title>Saved Snippets</title>
</head>
<body>
    <h2>Saved Snippets</h2>

    <ul>
        {% for snippet in snippets %}
            <li>
                <pre>{{ snippet[1] }}</pre>
                <button onclick="shareSnippet('{{ snippet[0] }}')">Share</button>
            </li>
        {% endfor %}
    </ul>

    <a href="/"><button>Back to Editor</button></a>

    <script>
        function shareSnippet(snippetId) {
            const link = window.location.origin + "/snippet/" + snippetId;
            alert("Share this link: " + link);
        }
    </script>
</body>
</html>
