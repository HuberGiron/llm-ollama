import argparse
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


MIN_ITERACIONES_RECOMENDADAS = 100


def cargar_csv(ruta_csv: str) -> pd.DataFrame:
    df = pd.read_csv(ruta_csv)

    columnas_numericas = [
        "cycle",
        "temperature",
        "top_p",
        "top_k",
        "min_p",
        "num_ctx",
        "num_predict",
        "repeat_penalty",
        "total_duration_s",
        "wall_time_s",
        "load_duration_s",
        "prompt_eval_count",
        "eval_count",
        "eval_duration_s",
        "tokens_per_second",
        "response_chars",
        "quality_score",
        "parameter_value",
    ]

    for col in columnas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "total_duration_s" not in df.columns:
        if "wall_time_s" in df.columns:
            df["total_duration_s"] = df["wall_time_s"]
        else:
            raise ValueError("El CSV necesita la columna total_duration_s o wall_time_s.")

    if "wall_time_s" in df.columns:
        df["total_duration_s"] = df["total_duration_s"].fillna(df["wall_time_s"])

    df["latency_ms"] = df["total_duration_s"] * 1000

    if "prompt_eval_count" in df.columns and "eval_count" in df.columns:
        df["total_tokens"] = df["prompt_eval_count"] + df["eval_count"]
    else:
        df["total_tokens"] = pd.NA

    if "tokens_per_second" not in df.columns:
        df["tokens_per_second"] = pd.NA

    if "eval_count" in df.columns and "eval_duration_s" in df.columns:
        tps_calculado = df["eval_count"] / df["eval_duration_s"]
        df["tokens_per_second"] = df["tokens_per_second"].fillna(tps_calculado)

    df = df.dropna(subset=["cycle", "latency_ms"])
    df = df[df["latency_ms"] > 0]

    return df


def detectar_modo(df: pd.DataFrame) -> str:
    if "parameter_changed" in df.columns and "parameter_value" in df.columns:
        if df["parameter_changed"].notna().any():
            return "parametros"

    return "modelos"


def crear_grupo(df: pd.DataFrame, modo: str) -> pd.DataFrame:
    df = df.copy()

    if modo == "modelos":
        df["grupo"] = df["model"].astype(str)

    elif modo == "parametros":
        df["grupo"] = (
            df["parameter_changed"].astype(str)
            + " = "
            + df["parameter_value"].astype(str)
        )

    return df


def obtener_conteo_iteraciones(df: pd.DataFrame) -> pd.DataFrame:
    conteo = (
        df.groupby("grupo")
        .agg(
            n_iteraciones=("cycle", "count"),
            ciclo_minimo=("cycle", "min"),
            ciclo_maximo=("cycle", "max"),
            latencia_media_ms=("latency_ms", "mean"),
            latencia_std_ms=("latency_ms", "std"),
        )
        .reset_index()
    )

    conteo["cumple_100_iteraciones"] = (
        conteo["n_iteraciones"] >= MIN_ITERACIONES_RECOMENDADAS
    )

    return conteo


def texto_n_iteraciones(grupo: str, conteo_iteraciones: pd.DataFrame) -> str:
    fila = conteo_iteraciones[conteo_iteraciones["grupo"] == grupo]

    if fila.empty:
        return ""

    n = int(fila.iloc[0]["n_iteraciones"])
    ciclo_min = int(fila.iloc[0]["ciclo_minimo"])
    ciclo_max = int(fila.iloc[0]["ciclo_maximo"])

    if n < MIN_ITERACIONES_RECOMENDADAS:
        return (
            f"n={n} iteraciones "
            f"(ciclos {ciclo_min}-{ciclo_max}; "
            f"muestra menor a {MIN_ITERACIONES_RECOMENDADAS})"
        )

    return f"n={n} iteraciones (ciclos {ciclo_min}-{ciclo_max})"


def imprimir_diagnostico(df: pd.DataFrame, conteo_iteraciones: pd.DataFrame) -> None:
    print("\nGrupos detectados e iteraciones reales:")
    print(conteo_iteraciones.to_string(index=False))

    if not conteo_iteraciones["cumple_100_iteraciones"].all():
        print("\nADVERTENCIA:")
        print(
            f"Uno o más grupos tienen menos de {MIN_ITERACIONES_RECOMENDADAS} "
            "iteraciones. Las gráficas son útiles para exploración, pero la "
            "comparación estadística es menos robusta."
        )

    n_unicos = conteo_iteraciones["n_iteraciones"].nunique()

    if n_unicos > 1:
        print("\nADVERTENCIA:")
        print(
            "Los grupos no tienen el mismo número de iteraciones. "
            "La comparación visual sigue siendo válida, pero las medias y "
            "desviaciones estándar deben interpretarse con cuidado."
        )


def resumen_estadistico(df: pd.DataFrame, out_dir: Path) -> None:
    columnas = {
        "cycle": ["count", "min", "max"],
        "latency_ms": ["mean", "std", "min", "max"],
        "prompt_eval_count": ["mean", "std", "min", "max"],
        "eval_count": ["mean", "std", "min", "max"],
        "total_tokens": ["mean", "std", "min", "max"],
        "tokens_per_second": ["mean", "std", "min", "max"],
    }

    if "quality_score" in df.columns:
        columnas["quality_score"] = ["mean", "std", "min", "max"]

    columnas_existentes = {
        col: funcs for col, funcs in columnas.items() if col in df.columns
    }

    resumen = df.groupby("grupo").agg(columnas_existentes)
    resumen.columns = ["_".join(c).strip() for c in resumen.columns]
    resumen = resumen.reset_index()

    resumen["cumple_100_iteraciones"] = (
        resumen["cycle_count"] >= MIN_ITERACIONES_RECOMENDADAS
    )

    resumen.to_csv(
        out_dir / "resumen_estadistico.csv",
        index=False,
        encoding="utf-8-sig",
    )

    print("\nResumen estadístico:")
    print(resumen.to_string(index=False))


def grafica_latencia_por_grupo(
    df: pd.DataFrame,
    out_dir: Path,
    conteo_iteraciones: pd.DataFrame,
) -> None:
    for grupo, data in df.groupby("grupo"):
        data = data.sort_values("cycle")

        media = data["latency_ms"].mean()
        sigma = data["latency_ms"].std()
        n_texto = texto_n_iteraciones(grupo, conteo_iteraciones)

        fig, ax = plt.subplots(figsize=(10, 7))

        ax.scatter(
            data["cycle"],
            data["latency_ms"],
            s=35,
            alpha=0.85,
            label="iteraciones",
        )

        ax.axhline(
            media,
            linestyle="--",
            linewidth=1.6,
            label=f"media = {media:.2f} ms",
        )

        if pd.notna(sigma):
            ax.fill_between(
                data["cycle"],
                media - sigma,
                media + sigma,
                alpha=0.20,
                label=f"±1σ = {sigma:.2f} ms",
            )

        in_tok = data["prompt_eval_count"].mean() if "prompt_eval_count" in data else None
        out_tok = data["eval_count"].mean() if "eval_count" in data else None

        token_text = ""
        if pd.notna(in_tok) and pd.notna(out_tok):
            token_text = f"\nin_tok≈{in_tok:.0f} out_tok≈{out_tok:.0f}"

        ax.set_title(
            f"Latencia por iteración\n"
            f"{grupo} | {n_texto}"
            f"{token_text}"
        )

        ax.set_xlabel("Iteración")
        ax.set_ylabel("Tiempo total (ms)")
        ax.grid(True)
        ax.legend()

        nombre = limpiar_nombre_archivo(grupo)
        fig.tight_layout()
        fig.savefig(out_dir / f"latencia_iteracion_{nombre}.png", dpi=160)
        plt.close(fig)


def grafica_todos_los_grupos_latencia(
    df: pd.DataFrame,
    out_dir: Path,
    conteo_iteraciones: pd.DataFrame,
) -> None:
    fig, ax = plt.subplots(figsize=(12, 7))

    for grupo, data in df.groupby("grupo"):
        data = data.sort_values("cycle")
        n = len(data)

        ax.plot(
            data["cycle"],
            data["latency_ms"],
            marker="o",
            linewidth=1.4,
            markersize=4,
            alpha=0.85,
            label=f"{grupo} (n={n})",
        )

    n_min = int(conteo_iteraciones["n_iteraciones"].min())
    n_max = int(conteo_iteraciones["n_iteraciones"].max())

    if n_min == n_max:
        subtitulo = f"n={n_min} iteraciones por grupo"
    else:
        subtitulo = f"n variable por grupo: mínimo={n_min}, máximo={n_max}"

    ax.set_title(f"Latencia por iteración comparando grupos\n{subtitulo}")
    ax.set_xlabel("Iteración")
    ax.set_ylabel("Tiempo total (ms)")
    ax.grid(True)
    ax.legend()

    fig.tight_layout()
    fig.savefig(out_dir / "latencia_iteracion_todos_los_grupos.png", dpi=160)
    plt.close(fig)


def grafica_todos_los_grupos_latencia_media(df: pd.DataFrame, out_dir: Path) -> None:
    resumen = (
        df.groupby("grupo")
        .agg(
            media=("latency_ms", "mean"),
            desviacion=("latency_ms", "std"),
            n=("cycle", "count"),
        )
        .reset_index()
        .sort_values("media")
    )

    labels = [
        f"{row.grupo}\n(n={int(row.n)})"
        for row in resumen.itertuples(index=False)
    ]

    fig, ax = plt.subplots(figsize=(12, 7))

    ax.bar(
        labels,
        resumen["media"],
        yerr=resumen["desviacion"],
        capsize=5,
        alpha=0.85,
    )

    ax.set_title("Latencia promedio por grupo con desviación estándar")
    ax.set_xlabel("Grupo")
    ax.set_ylabel("Tiempo promedio (ms)")
    ax.grid(True, axis="y")
    plt.xticks(rotation=25, ha="right")

    fig.tight_layout()
    fig.savefig(out_dir / "latencia_promedio_por_grupo.png", dpi=160)
    plt.close(fig)


def grafica_tokens_por_segundo(df: pd.DataFrame, out_dir: Path) -> None:
    if "tokens_per_second" not in df.columns:
        return

    data_plot = df.dropna(subset=["tokens_per_second"])

    if data_plot.empty:
        return

    fig, ax = plt.subplots(figsize=(12, 7))

    for grupo, data in data_plot.groupby("grupo"):
        data = data.sort_values("cycle")

        ax.plot(
            data["cycle"],
            data["tokens_per_second"],
            marker="o",
            linewidth=1.4,
            markersize=4,
            alpha=0.85,
            label=f"{grupo} (n={len(data)})",
        )

    ax.set_title("Tokens de salida por segundo")
    ax.set_xlabel("Iteración")
    ax.set_ylabel("Tokens/s")
    ax.grid(True)
    ax.legend()

    fig.tight_layout()
    fig.savefig(out_dir / "tokens_por_segundo_todos_los_grupos.png", dpi=160)
    plt.close(fig)


def grafica_latencia_vs_tokens_salida(df: pd.DataFrame, out_dir: Path) -> None:
    if "eval_count" not in df.columns:
        return

    data_plot = df.dropna(subset=["eval_count", "latency_ms"])

    if data_plot.empty:
        return

    fig, ax = plt.subplots(figsize=(12, 7))

    for grupo, data in data_plot.groupby("grupo"):
        ax.scatter(
            data["eval_count"],
            data["latency_ms"],
            s=45,
            alpha=0.75,
            label=f"{grupo} (n={len(data)})",
        )

    ax.set_title("Latencia respecto a tokens de salida")
    ax.set_xlabel("Tokens de salida")
    ax.set_ylabel("Tiempo total (ms)")
    ax.grid(True)
    ax.legend()

    fig.tight_layout()
    fig.savefig(out_dir / "latencia_vs_tokens_salida.png", dpi=160)
    plt.close(fig)


def grafica_latencia_vs_tokens_totales(df: pd.DataFrame, out_dir: Path) -> None:
    if "total_tokens" not in df.columns:
        return

    data_plot = df.dropna(subset=["total_tokens", "latency_ms"])

    if data_plot.empty:
        return

    fig, ax = plt.subplots(figsize=(12, 7))

    for grupo, data in data_plot.groupby("grupo"):
        ax.scatter(
            data["total_tokens"],
            data["latency_ms"],
            s=45,
            alpha=0.75,
            label=f"{grupo} (n={len(data)})",
        )

    ax.set_title("Latencia respecto a tokens totales")
    ax.set_xlabel("Tokens totales = entrada + salida")
    ax.set_ylabel("Tiempo total (ms)")
    ax.grid(True)
    ax.legend()

    fig.tight_layout()
    fig.savefig(out_dir / "latencia_vs_tokens_totales.png", dpi=160)
    plt.close(fig)


def grafica_boxplot_latencia(df: pd.DataFrame, out_dir: Path) -> None:
    grupos = list(df["grupo"].dropna().unique())

    if not grupos:
        return

    data = [df[df["grupo"] == grupo]["latency_ms"].dropna() for grupo in grupos]
    labels = [
        f"{grupo}\n(n={len(df[df['grupo'] == grupo])})"
        for grupo in grupos
    ]

    fig, ax = plt.subplots(figsize=(12, 7))

    ax.boxplot(data, labels=labels, showmeans=True)

    ax.set_title("Distribución de latencia por grupo")
    ax.set_xlabel("Grupo")
    ax.set_ylabel("Tiempo total (ms)")
    ax.grid(True, axis="y")
    plt.xticks(rotation=25, ha="right")

    fig.tight_layout()
    fig.savefig(out_dir / "boxplot_latencia_por_grupo.png", dpi=160)
    plt.close(fig)


def grafica_por_parametro(df: pd.DataFrame, out_dir: Path) -> None:
    if "parameter_changed" not in df.columns or "parameter_value" not in df.columns:
        return

    for parametro, data_param in df.groupby("parameter_changed"):
        if pd.isna(parametro):
            continue

        fig, ax = plt.subplots(figsize=(12, 7))

        for valor, data in data_param.groupby("parameter_value"):
            data = data.sort_values("cycle")

            ax.plot(
                data["cycle"],
                data["latency_ms"],
                marker="o",
                linewidth=1.4,
                markersize=4,
                alpha=0.85,
                label=f"{parametro}={valor} (n={len(data)})",
            )

        ax.set_title(f"Latencia por iteración variando {parametro}")
        ax.set_xlabel("Iteración")
        ax.set_ylabel("Tiempo total (ms)")
        ax.grid(True)
        ax.legend()

        fig.tight_layout()
        fig.savefig(
            out_dir / f"latencia_variando_{limpiar_nombre_archivo(str(parametro))}.png",
            dpi=160,
        )
        plt.close(fig)


def limpiar_nombre_archivo(texto: str) -> str:
    texto = str(texto)

    reemplazos = {
        "/": "_",
        "\\": "_",
        ":": "_",
        " ": "_",
        ".": "_",
        "=": "_",
        ",": "_",
        "(": "",
        ")": "",
    }

    for viejo, nuevo in reemplazos.items():
        texto = texto.replace(viejo, nuevo)

    return texto.lower()


def main():
    parser = argparse.ArgumentParser(
        description="Genera gráficas de benchmark de LLM con Ollama."
    )

    parser.add_argument(
        "--csv",
        required=True,
        help="Archivo CSV de entrada.",
    )

    parser.add_argument(
        "--out",
        default="graficas_benchmark",
        help="Carpeta de salida.",
    )

    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = cargar_csv(args.csv)
    modo = detectar_modo(df)
    df = crear_grupo(df, modo)

    conteo_iteraciones = obtener_conteo_iteraciones(df)

    print(f"\nArchivo leído: {args.csv}")
    print(f"Modo detectado: {modo}")
    print(f"Filas válidas: {len(df)}")

    imprimir_diagnostico(df, conteo_iteraciones)

    resumen_estadistico(df, out_dir)

    grafica_latencia_por_grupo(df, out_dir, conteo_iteraciones)
    grafica_todos_los_grupos_latencia(df, out_dir, conteo_iteraciones)
    grafica_todos_los_grupos_latencia_media(df, out_dir)
    grafica_tokens_por_segundo(df, out_dir)
    grafica_latencia_vs_tokens_salida(df, out_dir)
    grafica_latencia_vs_tokens_totales(df, out_dir)
    grafica_boxplot_latencia(df, out_dir)

    if modo == "parametros":
        grafica_por_parametro(df, out_dir)

    print(f"\nGráficas guardadas en: {out_dir.resolve()}")


if __name__ == "__main__":
    main()

