pip install jupyter-book[plotly]
pip install ghp-import
jupyter-book build .
# Delete the remote gh-pages branch
git push origin --delete gh-pages
# Import and force push (this creates a fresh branch each time)
ghp-import -n -p -f _build/
git checkout gh-pages
echo '<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0; url=https://fusion-energy.github.io/neutronics-workshop/html/docs/index.html">
    <title>Redirecting...</title>
</head>
<body>
    <p>If you are not redirected automatically, follow this <a href="https://fusion-energy.github.io/neutronics-workshop/html/docs/index.html">link</a>.</p>
</body>
</html>' > index.html
git add index.html
git commit -m 'added redirect index'
git push