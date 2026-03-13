
import cv2
import numpy as np

def detect_rh_factor(rgb_uint8: np.ndarray) -> str:
    """
    Heuristic Rh factor detection based on 'agglutination-like' texture analysis.
    In a real system, this would be a trained classifier or an analysis of the 'D' spot.
    Here we use Laplacian variance as a proxy for graininess/agglutination.
    """
    gray = cv2.cvtColor(rgb_uint8, cv2.COLOR_RGB2GRAY)
    
    # Calculate Laplacian variance - a measure of 'edge' density or granularity
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    # Heuristic threshold: agglutinated blood is grainier/sharper than smooth blood.
    # Note: These values are purely illustrative for the demo.
    RH_THRESHOLD = 150.0 
    
    if laplacian_var > RH_THRESHOLD:
        return "+"
    else:
        return "-"

def get_rh_confidence(rgb_uint8: np.ndarray) -> float:
    # Scale the laplacian variance to a 0-1 confidence for demonstration
    gray = cv2.cvtColor(rgb_uint8, cv2.COLOR_RGB2GRAY)
    v = cv2.Laplacian(gray, cv2.CV_64F).var()
    # Sigmoid-like mapping
    conf = 1.0 / (1.0 + np.exp(-(v - 150.0) / 30.0))
    return float(max(0.6, conf) if conf > 0.5 else max(0.6, 1.0 - conf))
