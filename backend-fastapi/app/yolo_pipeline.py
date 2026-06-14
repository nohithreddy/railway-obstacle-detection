from pathlib import Path


def training_command(data_yaml: str = "datasets/railway/data.yaml", epochs: int = 80) -> str:
    return f"yolo detect train model=yolov8n.pt data={data_yaml} epochs={epochs} imgsz=640"


def export_command(weights_path: str = "runs/detect/train/weights/best.pt") -> str:
    return f"yolo export model={weights_path} format=onnx dynamic=True simplify=True"


def write_dataset_yaml(base_dir: Path) -> Path:
    yaml_path = base_dir / "data.yaml"
    yaml_path.write_text(
        "\n".join(
            [
                "path: datasets/railway",
                "train: images/train",
                "val: images/val",
                "names:",
                "  0: person",
                "  1: animal",
                "  2: motorcycle",
                "  3: car",
                "  4: truck",
                "  5: bus",
                "  6: fallen_tree",
                "  7: rockslide",
                "  8: debris",
                "  9: track_damage",
            ]
        ),
        encoding="utf-8",
    )
    return yaml_path
