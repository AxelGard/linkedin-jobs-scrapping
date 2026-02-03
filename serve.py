#!./env/bin/python3
import os
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Collect job postings data from Linkedin."
    )
    parser.add_argument(
        "--input",
        default="./img/",
        type=str,
        help="input path (defualt: ./results/)",
    )

    args = parser.parse_args()
    path = args.input

    
    for p in [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]:
        location, title = p.split("-")
        print(title)


    with open(f"{path}index.html", "w") as f:
        imgs = "\n".join([f'<a href="./{p}">{p}<br>' for p in [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]])
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Linkedin Job data </title>
</head>
<body>
    <h1>Linkedin Job data from {location}</h1>
    <br>
    {imgs}
</body>
</html>
        """
        f.write(html)

    os.system("cp -fR ./img/* /var/www/linkdata/")
    return 0

if __name__ == "__main__":
    main()