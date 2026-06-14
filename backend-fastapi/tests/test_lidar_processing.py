from app.lidar_processing import LidarPoint, nearest_track_cluster


def test_nearest_track_cluster_ignores_off_track_points():
    result = nearest_track_cluster(
        [
            LidarPoint(x=3.0, y=10.0, z=0.5),
            LidarPoint(x=0.1, y=20.0, z=0.2),
            LidarPoint(x=0.2, y=12.0, z=1.0),
        ]
    )

    assert result is not None
    assert result["track_position"] == "center"
    assert result["distance_m"] < 13
