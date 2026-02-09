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
        links = "\n".join([f'<a style="font-family: Arial, sans-serif;" href="./{p}">{p}</a><br>' for p in [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]])
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Linkedin Job data </title>
</head>
<body>
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/aa/LinkedIn_2021.svg/500px-LinkedIn_2021.svg.png">
    <br>
    <h1 style="font-family: Arial, sans-serif;">Linkedin Job data from {location}</h1>
    <br>
    {links}
</body>
</html>
        """
        f.write(html)

    if not debugging:
        os.system(f"cp -fR {path}* /var/www/linkdata/")
    return 0

if __name__ == "__main__":
    main()
