import marimo

__generated_with = "0.12.7"
app = marimo.App()


@app.cell
def _():
    # Ungleichheiten in deutschen Städten
    return


@app.cell(disabled=True, hide_code=True)
def _(mo):
    mo.md(r"""### CSV-Datei einlesen""")
    return


@app.cell
def _():
    import pandas as pd

    df = pd.read_csv(
        "data/ungleichheiten.csv",
        header=0,
        delimiter=";",
    )
    # df.head
    return df, pd


@app.cell(disabled=True, hide_code=True)
def _(mo):
    mo.md(r"""### Fehlende Werte behandeln""")
    return


@app.cell
def _(df):
    df_1 = df.fillna(-1)
    return (df_1,)


@app.cell(disabled=True, hide_code=True)
def _(mo):
    mo.md(r"""### Spaltennamen ändern""")
    return


@app.cell
def _(df_1):
    df_1.rename(
        columns={
            "bev_ges_zelle": "Einwohner pro qkm",
            "sgb_quote": "Armutsquote",
            "akad_ant_zelle": "Anteil Akademiker",
            "ant_elb_zelle": "Anteil SGB II Empfänger",
            "ant_4800ein_zelle": "Einkommen > 4800",
            "ant_6600ein_zelle": "Einkommen > 6600",
        },
        inplace=True,
    )
    return


@app.cell(disabled=True, hide_code=True)
def _(mo):
    mo.md(r"""### Gitterkoordinaten extrahieren und Länge und Breite umwandeln""")
    return


@app.cell(hide_code=True)
def _(df_1):
    """
    Die Koordinaten der Spalte "gitter1km" sind im Format "1kmN3254E4569" (Lambert-Projektion ETRS89-LAEA (EPSG:3035))
    Sie müssen fur die Hintergrundkarte in WGS84 (EPSG:4326) umgerechnet werden
    """

    def extract_coords(gitter_id):
        parts = gitter_id.split("km")[1].split("N")[1].split("E")
        e = int(parts[0]) * 1000
        n = int(parts[1]) * 1000
        return (n, e)

    df_1["n"] = df_1["gitter1km"].apply(lambda x: extract_coords(x)[0])
    df_1["e"] = df_1["gitter1km"].apply(lambda x: extract_coords(x)[1])

    "\nDas ETRS89-LAEA-System verwendet False Easting und False Northing von 4321000 bzw. 3210000 Metern. \nUm die Koordinaten korrekt zu transformieren, werden diese Werte addiert\n"

    df_1["x"] = df_1["n"] + 4321000
    df_1["y"] = df_1["e"] + 3210000
    import pyproj

    etrs_laea = pyproj.Proj("epsg:3035")
    wgs84 = pyproj.Proj("epsg:4326")
    (df_1["lat"], df_1["lon"]) = pyproj.transform(
        etrs_laea, wgs84, df_1["x"], df_1["y"]
    )
    return etrs_laea, extract_coords, pyproj, wgs84


@app.cell
def _(mo):
    mo.md(r"""### 1. Stadt auswählen""")
    return


@app.cell
def _(df_1, mo):
    # Nur den Stadtnamen vor dem Komma extrahieren
    df_1["stadt"] = df_1["gemeindename"].str.extract("^(.*?),")

    # Nur erste Zeile der jeweiligen Stadt alphabetisch
    df_1.sort_values("stadt", ascending=True, inplace=True)
    staedte = df_1["stadt"].unique()

    # Dropdown mit allen Städten
    drop_stadt = mo.ui.dropdown(options=staedte, value="Berlin")
    drop_stadt
    return drop_stadt, staedte


@app.cell(disabled=True, hide_code=True)
def _(mo):
    mo.md(r"""### Stadt extrahieren""")
    return


@app.cell
def _(df_1, drop_stadt):
    # Wert aus Dropdownliste auswaehlen
    stadt = [drop_stadt.value]

    # Nur Daten von ausgewaehlten Stadten ausgeben
    gemeinde_stadt = df_1[df_1["stadt"].isin(stadt)]

    # print(drop_stadt.value)
    # gemeinde_stadt
    return gemeinde_stadt, stadt


@app.cell
def _(mo):
    mo.md("""### 2. Jahr auswählen""")
    return


@app.cell
def _(gemeinde_stadt, mo):
    # Nur erste Zeile des jeweiligen Jahres aufsteigend
    gemeinde_stadt.sort_values("jahr", ascending=True, inplace=True)
    jahre = gemeinde_stadt["jahr"].unique()

    # Dropdown mit allen verfuegbaren Jahren
    drop_jahr = mo.ui.dropdown(
        options=jahre.astype(str), value=jahre[len(jahre) - 1].astype(str)
    )
    drop_jahr
    return drop_jahr, jahre


@app.cell
def _(drop_jahr, gemeinde_stadt):
    # Neuer Dataframe mit nur den Daten des jeweiligen Jahres
    gemeinde_df = gemeinde_stadt[
        gemeinde_stadt["jahr"].isin([drop_jahr.value.astype(int)])
    ]
    # print([drop_jahr.value])
    # gemeinde_df
    return (gemeinde_df,)


@app.cell(disabled=True, hide_code=True)
def _(mo):
    mo.md(r"""### GeoDataFrames mit Geopandas erstellen""")
    return


@app.cell
def _(gemeinde_df):
    import geopandas as gpd

    # Erstelle einen GeoDataFrame mit Geopandas fur die Daten der Tabelle (EPSG:3035)
    gdf = gpd.GeoDataFrame(
        gemeinde_df, geometry=gpd.points_from_xy(gemeinde_df["n"], gemeinde_df["e"])
    )

    # Erstelle einen GeoDataFrame mit Geopandas fur die Hintergrundkarte (EPSG:4326)
    ctx_gdf = gpd.GeoDataFrame(
        geometry=gpd.points_from_xy(
            gemeinde_df["lat"], gemeinde_df["lon"], crs="EPSG:3035"
        ),
    )

    # gdf.head
    return ctx_gdf, gdf, gpd


@app.cell
def _(mo):
    mo.md(r"""### 3. Daten für die Visualisierung auswählen""")
    return


@app.cell
def _(mo):
    # Gitterdaten
    spalten = [
        "Einwohner pro qkm",
        "Armutsquote",
        "Anteil Akademiker",
        "Anteil SGB II Empfänger",
        "Einkommen > 4800",
        "Einkommen > 6600",
    ]

    # Dropdown mit allen verfuegbaren Gitterdaten fuer Punktgröße
    drop_groesse = mo.ui.dropdown(
        options=spalten, value="Einwohner pro qkm", label="Punktgröße: "
    )
    drop_groesse
    return drop_groesse, spalten


@app.cell
def _(mo, spalten):
    # Dropdown mit allen verfügbaren Gitterdaten fuer Farbe
    drop_farbe = mo.ui.dropdown(options=spalten, value="Armutsquote", label="Farbe: ")
    drop_farbe
    return (drop_farbe,)


@app.cell(disabled=True, hide_code=True)
def _(mo):
    mo.md(r"""### Visualisierung""")
    return


@app.cell
def _(ctx_gdf, drop_farbe, drop_groesse, gdf, gemeinde_df):
    import matplotlib.pyplot as plt
    import contextily as ctx

    # import cartopy
    # import cartopy.crs as ccrs

    # Umwandeln in WGS84 (EPSG:4326) mit der Geopandas-Funktion to_crs (Coordinate Reference System)
    back_gdf = ctx_gdf.to_crs(epsg=3857)
    # print(back_gdf.crs)

    # Visualisierung mit Matplotlib
    fig, ax = plt.subplots(figsize=(8, 10), dpi=200)

    spalte_farbe = drop_farbe.value
    spalte_groesse = drop_groesse.value

    farbe = gemeinde_df[spalte_farbe]  # Spalte der Farbe der Markierungen darstellt
    groesse = gemeinde_df[spalte_groesse]  # Spalte der Größe der Markierungen
    label = spalte_farbe  # Label fur Farblegende
    titel = (
        spalte_groesse
        + " (Punktgröße) und "
        + spalte_farbe
        + " (Farbe) der Stadt "
        + gemeinde_df["stadt"].iloc[0]
        + " im Jahr "
        + gemeinde_df["jahr"].iloc[0].astype(str)
    )

    gdf.plot(
        ax=ax,
        column=farbe,  # Spalte, die die Farbe der Markierungen darstellt
        cmap="OrRd",  # color map
        legend=True,  # Farblegende
        legend_kwds={
            "label": (label, gemeinde_df["jahr"].iloc[0].item()),
            "orientation": "horizontal",
        },
        markersize=groesse / 2e2,  # Größe der Punkte
    )

    plt.suptitle(titel, fontsize=8)  # Titel für den gesamten Plot
    ax.get_xaxis().set_ticklabels([])  # Entfernt die x-Ticks
    plt.yticks([])  # Entfernt die y-Tick-Labels
    # plt.xlabel("km*10", fontsize=8)  # Beschriftung der x-Achse

    # Hintergrundkarte hinzufügen
    ctx.add_basemap(
        ax, source=ctx.providers.OpenStreetMap.Mapnik, crs=ctx_gdf.crs, zoom=13
    )

    # plt.show()

    # Mache den Plot interaktiv
    # interactive_plot = mo.mpl.interactive(fig)
    # interactive_plot
    ax
    return (
        ax,
        back_gdf,
        ctx,
        farbe,
        fig,
        groesse,
        label,
        plt,
        spalte_farbe,
        spalte_groesse,
        titel,
    )


@app.cell
def _():
    import marimo as mo

    return (mo,)


if __name__ == "__main__":
    app.run()
