from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from astropy import units as u
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_horizontal_coords(ra: float, dec: float, lat: float, lon: float, alt: float, temp: float, pressure: float, time: Time):
    """
    Calculates the topocentric, apparent horizontal coordinates (Azimuth, Altitude)
    for a celestial object.

    This function uses astropy to handle all necessary astronomical transformations,
    including precession, nutation, aberration, and atmospheric refraction.

    Args:
        ra (float): Right Ascension of the target (in degrees).
        dec (float): Declination of the target (in degrees).
        lat (float): Observer's latitude (in degrees).
        lon (float): Observer's longitude (in degrees).
        alt (float): Observer's altitude (in meters).
        temp (float): Ambient temperature (in Celsius).
        pressure (float): Atmospheric pressure (in hPa or mbar).
        time (astropy.time.Time): The time of observation.

    Returns:
        astropy.coordinates.AltAz: An object containing the calculated
                                   Azimuth and Altitude.
    """
    try:
        # Define the observer's location on Earth
        location = EarthLocation(lat=lat*u.deg, lon=lon*u.deg, height=alt*u.m)

        # Define the celestial target's mean coordinates (ICRS, J2000)
        target_coords = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, frame='icrs')

        # Define the atmospheric conditions for refraction correction
        # astropy wants pressure in hPa/mbar and temperature in Celsius
        pressure_hpa = pressure * u.hPa
        temperature_c = temp * u.deg_C

        # Create the AltAz frame for the given time and location
        altaz_frame = AltAz(obstime=time, location=location,
                            pressure=pressure_hpa, temperature=temperature_c)

        # Transform the target's coordinates to the AltAz frame.
        # This single call performs all necessary transformations.
        horizontal_coords = target_coords.transform_to(altaz_frame)

        logging.info(f"Successfully transformed ICRS({ra},{dec}) to AltAz({horizontal_coords.az.deg:.4f}, {horizontal_coords.alt.deg:.4f})")

        return horizontal_coords

    except Exception as e:
        logging.error(f"Error during coordinate transformation: {e}")
        return None

# Example usage (for testing purposes)
if __name__ == '__main__':
    # Jakokoski observatory parameters (example values)
    jakokoski_lat = 62.727
    jakokoski_lon = 29.996
    jakokoski_alt = 155

    # Example atmospheric conditions
    temperature = -10.0 # Celsius
    pressure = 1013.0 # hPa

    # Get the current time
    now = Time.now()

    # Coordinates for a bright star, e.g., Vega (alpha Lyrae)
    # RA: 18h 36m 56.3s -> 279.23458 degrees
    # Dec: +38d 47m 01s -> 38.78361 degrees
    vega_ra = 279.23458
    vega_dec = 38.78361

    print(f"Calculating position for Vega at {now} from Jakokoski.")

    altaz_coords = get_horizontal_coords(
        ra=vega_ra,
        dec=vega_dec,
        lat=jakokoski_lat,
        lon=jakokoski_lon,
        alt=jakokoski_alt,
        temp=temperature,
        pressure=pressure,
        time=now
    )

    if altaz_coords:
        print(f"Result -> Azimuth: {altaz_coords.az:.4f}, Altitude: {altaz_coords.alt:.4f}")
