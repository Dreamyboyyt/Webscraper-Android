import os
import requests
from bs4 import BeautifulSoup
from rich.console import Console

console = Console()

# Configure storage location
STORAGE_DIR = "/storage/emulated/0/webscraper"

def setup_storage():
    """Create storage directory if it doesn't exist"""
    try:
        os.makedirs(STORAGE_DIR, exist_ok=True)
        console.print(f"[green]Using storage: {STORAGE_DIR}[/green]")
        return True
    except Exception as e:
        console.print(f"[red]Storage error: {e}[/red]")
        return False

def get_safe_filename(url, extension=".txt"):
    """Generate a valid filename from URL"""
    base = "".join(c if c.isalnum() else "_" for c in url.split("//")[-1].split("/")[0])
    return f"{base[:30]}_{os.path.basename(url)[:10]}{extension}"

def normal_scrape(url):
    """Scrape title and heading tags"""
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        title = soup.title.string if soup.title else "No Title Found"
        headings = [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3'])]
        
        content = f"URL: {url}\nTitle: {title}\n\nHeadings:\n"
        content += "\n".join(f"- {h}" for h in headings) if headings else "No headings found"
        
        return content, None
        
    except Exception as e:
        return None, f"Scraping failed: {e}"

def source_code_scrape(url):
    """Get raw HTML source code"""
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        resp.raise_for_status()
        return resp.text, None
    except Exception as e:
        return None, f"Source code fetch failed: {e}"

def save_results(content, filename):
    """Save content to specified file"""
    try:
        filepath = os.path.join(STORAGE_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return filepath, None
    except Exception as e:
        return None, f"Save failed: {e}"

def get_file_extension(mode):
    """Get format choice from user with .html enforcement for source code"""
    if mode == "1":
        console.print("\n[bold]Select Format:[/bold]")
        console.print("1. Text File (.txt)")
        console.print("2. CSV File (.csv)")
        choice = input("Choose format (1/2): ").strip()
        return ".csv" if choice == "2" else ".txt"
    else:
        # Source code mode - always save as .html by default
        console.print("\n[bold]Save Source Code As:[/bold]")
        console.print("1. HTML File (.html) [Recommended]")
        console.print("2. Text File (.txt)")
        choice = input("Choose format (1/2): ").strip()
        return ".html" if choice == "1" else ".txt"

def main():
    if not setup_storage():
        return

    url = input("Enter URL (include http/https): ").strip()
    if not url.startswith(('http://', 'https://')):
        console.print("[red]Invalid URL format[/red]")
        return

    console.print("\n[bold]Modes:[/bold]")
    console.print("1. Normal Scrape (Title & Headings)")
    console.print("2. Source Code Scrape")
    mode = input("Choose mode (1/2): ").strip()

    if mode == '1':
        content, error = normal_scrape(url)
    elif mode == '2':
        content, error = source_code_scrape(url)
    else:
        console.print("[red]Invalid choice[/red]")
        return

    if error:
        console.print(f"[red]{error}[/red]")
        return

    ext = get_file_extension(mode)
    filename = get_safe_filename(url, ext)
    
    # Format conversion only for normal scrape CSV
    if mode == "1" and ext == ".csv":
        lines = content.split('\n')
        csv_content = "Type,Content\n"
        csv_content += f"Title,{lines[1].replace('Title: ', '')}\n"
        for line in lines[4:]:
            if line.startswith('-'):
                csv_content += f"Heading,{line[2:]}\n"
        content = csv_content

    filepath, save_error = save_results(content, filename)
    
    if save_error:
        console.print(f"[red]{save_error}[/red]")
    else:
        console.print(f"\n[bold green]Success![/bold green]")
        console.print(f"File saved to: [cyan]{filepath}[/cyan]")
        console.print(f"Size: [yellow]{os.path.getsize(filepath)/1024:.1f} KB[/yellow]")
        if mode == "2" and ext == ".html":
            console.print("[yellow]Note: For proper HTML rendering, use a web browser[/yellow]")

if __name__ == "__main__":
    main()
