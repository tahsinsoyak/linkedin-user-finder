# LinkedIn User Finder

LinkedIn User Finder is a Python-based web scraping tool that automates the process of finding LinkedIn profiles based on specific keywords (e.g., company name and job position). It extracts profile data such as name, headline, location, and email (or generates potential email variations) and saves the results to a CSV file.

## Features

- Automated login to LinkedIn using credentials stored in environment variables.
- Search for LinkedIn profiles based on keywords (e.g., company name and job title).
- Extract profile details such as name, headline, location, and email.
- Generate potential email variations if no email is found.
- Save extracted data to a CSV file.
- Randomized delays to mimic human behavior and reduce the risk of detection.

## Prerequisites

- Python 3.7 or higher
- Google Chrome browser
- ChromeDriver (compatible with your Chrome version)
- A LinkedIn account
- `.env` file with your LinkedIn credentials

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/linkedin-user-finder.git
   cd linkedin-user-finder
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project directory and add your LinkedIn credentials:
   ```
   LINKEDIN_EMAIL=your-email@example.com
   LINKEDIN_PASSWORD=your-password
   ```

4. Download and install ChromeDriver:
   - [Download ChromeDriver](https://sites.google.com/chromium.org/driver/)
   - Ensure the `chromedriver` executable is in your system's PATH or the project directory.

## Usage

1. Run the script:
   ```bash
   python main.py
   ```

2. Enter the company name when prompted.

3. The script will search for profiles matching the specified company and job positions (e.g., "Export Manager").

4. Extracted profile data will be saved to a CSV file named `linkedin_profiles_<company>.csv`.

## Example Output

The CSV file will contain the following columns:
- `name`
- `headline`
- `location`
- `company`
- `email`
- `potential_emails` (if no email is found)

## Notes

- This tool uses Selenium for browser automation and BeautifulSoup for web scraping.
- Randomized delays are implemented to reduce the risk of detection by LinkedIn.
- Use this tool responsibly and ensure compliance with LinkedIn's terms of service.

## Troubleshooting

- If the script fails to log in, verify your credentials in the `.env` file.
- Ensure that ChromeDriver is installed and matches your Chrome browser version.
- If no profiles are found, try refining your search keywords.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is for educational purposes only. The author is not responsible for any misuse of this tool.