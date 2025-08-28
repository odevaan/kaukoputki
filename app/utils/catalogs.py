import logging
from astropy.coordinates import Angle
from astropy import units as u

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_ra(ra_str: str) -> float:
    """Parses an RA string (h m s) into decimal degrees."""
    try:
        # RA is in h m s format
        h, m, s = ra_str.split()
        # Use astropy's Angle to handle the conversion correctly
        angle = Angle(f"{h}h{m}m{s}s")
        return angle.degree
    except Exception as e:
        logging.error(f"Could not parse RA string: '{ra_str}'. Error: {e}")
        return None

def parse_dec(dec_str: str) -> float:
    """Parses a Dec string (+/-d m s) into decimal degrees."""
    try:
        # Dec is in d m s format, with sign
        sign = -1 if dec_str.startswith('-') else 1
        d, m, s = dec_str.lstrip('+-').split()
        # Use astropy's Angle for robust conversion
        angle = Angle(f"{sign*int(d)}d{m}m{s}s")
        return angle.degree
    except Exception as e:
        logging.error(f"Could not parse Dec string: '{dec_str}'. Error: {e}")
        return None

def load_messier_catalog(filepath: str):
    """
    Loads and parses the Messier catalog from a pipe-delimited file.

    Args:
        filepath (str): The path to the messier.cat file.

    Returns:
        list: A list of dictionaries, where each dictionary represents an object.
              Returns an empty list if the file cannot be read.
    """
    catalog = []
    try:
        with open(filepath, 'r', encoding='latin-1') as f:
            # Skip the header line
            next(f)
            for line in f:
                if not line.strip():
                    continue

                try:
                    # Split the line by the pipe delimiter
                    parts = [p.strip() for p in line.split('|')]

                    # Ensure we have enough parts to avoid IndexError
                    if len(parts) < 8:
                        logging.warning(f"Skipping malformed line: '{line.strip()}'")
                        continue

                    m_num_str = parts[0].replace('M','').strip()
                    m_num = int(m_num_str)

                    ra_str = parts[1]
                    dec_str = parts[2]
                    obj_type = parts[3]
                    constellation = parts[4]
                    size_str = parts[5]
                    mag_str = parts[6]
                    desc = parts[7]

                    # Convert coordinates to decimal degrees
                    ra_deg = parse_ra(ra_str)
                    dec_deg = parse_dec(dec_str)

                    if ra_deg is None or dec_deg is None:
                        logging.warning(f"Skipping M{m_num} due to coordinate parsing error.")
                        continue

                    catalog.append({
                        "name": f"M{m_num}",
                        "m_num": m_num,
                        "ra_deg": ra_deg,
                        "dec_deg": dec_deg,
                        "type": obj_type,
                        "constellation": constellation,
                        "size": float(size_str) if size_str else None,
                        "magnitude": float(mag_str) if mag_str and 'p' not in mag_str else None,
                        "description": desc
                    })
                except (ValueError, IndexError) as e:
                    logging.error(f"Failed to parse line: '{line.strip()}'. Error: {e}")
                    continue

        logging.info(f"Successfully loaded {len(catalog)} objects from {filepath}")
        return catalog

    except FileNotFoundError:
        logging.error(f"Catalog file not found at {filepath}")
        return []

# Example usage (for testing purposes)
if __name__ == '__main__':
    # This assumes the script is run from the root of the project
    messier_file = 'matlab_code/messier.cat'
    messier_catalog = load_messier_catalog(messier_file)

    if messier_catalog:
        print(f"Loaded {len(messier_catalog)} Messier objects.")
        # Print details for M31 (Andromeda Galaxy)
        m31 = next((item for item in messier_catalog if item["m_num"] == 31), None)
        if m31:
            print("\nExample object (M31):")
            print(m31)
