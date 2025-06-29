import osmnx as ox
import matplotlib.pyplot as plt


def get_green_spaces(city_name):
    """
    Fetches green space data for a given city from OpenStreetMap.
    """
    print(f"Fetching data for {city_name}...")
    # Defined the tags for green spaces in OpenStreetMap
    tags = {
        "leisure": ["park", "garden", "playground"],
        "landuse": ["forest", "grass", "recreation_ground"],
        "natural": ["wood", "scrub", "heath"],
    }

    gdf = ox.features_from_place(city_name, tags)

    print(f"Found {len(gdf)} green spaces in {city_name}.")
    return gdf


def plot_city_green_spaces(gdf, city_name):
    """
    Plots the fetched green spaces on a simple map.
    """
    # Reprojects to a suitable CRS for accurate plotting
    gdf_proj = gdf.to_crs(epsg=3857)

    # Creates the plot
    fig, ax = plt.subplots(figsize=(12, 12))
    gdf_proj.plot(ax=ax, facecolor="green")

    # Removes axis for a cleaner look
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(f"Green Spaces in {city_name}", fontsize=16)

    # Saves the plot to a file
    # Creating a simple filename from the city name
    filename_city = city_name.split(',')[0].replace(' ', '_')
    plt.savefig(f"{filename_city}_map.png", dpi=300)
    print(f"Map saved as {filename_city}_map.png")
    plt.show()  # Displays the plot


# --- Main execution block ---
if __name__ == "__main__":
    # I can change this to any city in the world!
    # "Lisbon, Portugal", "Tokyo, Japan", or my hometown.
    target_city = "Helsinki, Finland"

    green_spaces_gdf = get_green_spaces(target_city)

    if not green_spaces_gdf.empty:
        plot_city_green_spaces(green_spaces_gdf, target_city)