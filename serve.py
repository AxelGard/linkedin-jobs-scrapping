#!./env/bin/python3
import os
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Collect job postings data from Linkedin."
    )
    parser.add_argument(
        "--input",
        default="./www/",
        type=str,
        help="input path (defualt: ./results/)",
    )

    parser.add_argument(
        "--location",
        "-l",
        default="Linköping",
        type=str,
        help="input path (defualt: Linköping)",
    )

    parser.add_argument(
        '--debug', 
        '-d',
        action='store_true'
    )

    args = parser.parse_args()
    path = args.input
    location = args.location
    debugging = args.debug

    if path[-1] != "/":
        path += "/"
    
    for p in [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]:
        location, title = p.split("-")
        print(title)


    with open(f"{path}index.html", "w") as f:
        links = "\n".join([f'<li><a style="font-family: Arial, sans-serif;" href="./{p}">{p}</a></li>' for p in [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]])
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Linkedin Job data </title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB" crossorigin="anonymous">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js" integrity="sha384-FKyoEForCGlyvwx9Hj09JcYn3nv7wiPVlz7YYwJrWVcXK/BmnVDxM+D2scQbITxI" crossorigin="anonymous"></script>
</head>
<body>

        <br>
        <div class="container">
          <div class="row">

            <div class="col">
            </div>

            <div class="col-8">
                <br>
                <h1 style="font-family: Arial, sans-serif;">Linkedin Job data</h1>
                <br>
                <ul>
                    {links}
                </ul>
            </div>

            <div class="col">
            </div>

          </div>
        </div>
    
</body>
</html>
        """
        f.write(html)

    if not debugging:
        os.system(f"cp -fR {path}* /var/www/linkdata/")
    return 0

if __name__ == "__main__":
    main()
