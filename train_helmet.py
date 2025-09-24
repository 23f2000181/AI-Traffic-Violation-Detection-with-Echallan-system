from ultralytics import YOLO
import os

def train_helmet_model():
    """Train YOLOv8 model on helmet dataset"""

    # Load pre-trained YOLOv8 nano model
    model = YOLO("yolov8n.pt")

    # Training configuration
    training_config = {
        'data': 'datasets/helmet/data.yaml',  # Path to dataset config
        'epochs': 50,                        # Number of training epochs
        'batch': 16,                         # Batch size (adjust based on your RAM)
        'imgsz': 640,                        # Image size
        'device': 'cpu',                     # Use CPU (change to '0' for GPU)
        'workers': 4,                        # Number of worker threads
        'patience': 10,                      # Early stopping patience
        'save': True,                        # Save model checkpoints
        'project': 'runs/detect',            # Project directory
        'name': 'helmet_detection',          # Experiment name
        'exist_ok': True,                    # Overwrite existing runs
        'pretrained': True,                  # Use pre-trained weights
        'optimizer': 'Adam',                 # Optimizer
        'lr0': 0.001,                        # Initial learning rate
        'lrf': 0.01,                         # Final learning rate
        'momentum': 0.937,                   # SGD momentum
        'weight_decay': 0.0005,              # Weight decay
        'warmup_epochs': 3,                  # Warmup epochs
        'warmup_momentum': 0.8,              # Warmup momentum
        'warmup_bias_lr': 0.1,               # Warmup bias learning rate
        'box': 7.5,                          # Box loss weight
        'cls': 0.5,                          # Classification loss weight
        'dfl': 1.5,                          # DFL loss weight
        'fl_gamma': 0.0,                     # Focal loss gamma
        'label_smoothing': 0.0,              # Label smoothing
        'nbs': 64,                           # Nominal batch size
        'overlap_mask': True,                # Mask overlap
        'mask_ratio': 4,                     # Mask ratio
        'dropout': 0.0,                      # Dropout rate
        'val': True,                         # Validate during training
        'plots': True,                       # Create plots
        'save_period': 10,                   # Save checkpoint every N epochs
        'cache': False,                      # Cache images
        'rect': False,                       # Rectangular training
        'cos_lr': False,                     # Cosine learning rate
        'close_mosaic': 10,                  # Close mosaic augmentation
        'resume': False,                     # Resume training
        'amp': True,                         # Automatic mixed precision
        'fraction': 1.0,                     # Dataset fraction
        'profile': False,                    # Profile training
        'freeze': None,                      # Freeze layers
        'multi_scale': False,                # Multi-scale training
        'overlap_mask': True,                # Overlap masks
        'mask_ratio': 4,                     # Mask ratio
        'dropout': 0.0,                      # Dropout
        'val': True,                         # Validation
        'plots': True,                       # Plots
        'save_period': 10,                   # Save period
        'cache': False,                      # Cache
        'rect': False,                       # Rectangular
        'cos_lr': False,                     # Cosine LR
        'close_mosaic': 10,                  # Close mosaic
        'resume': False,                     # Resume
        'amp': True,                         # AMP
        'fraction': 1.0,                     # Fraction
        'profile': False,                    # Profile
        'freeze': None,                      # Freeze
        'multi_scale': False,                # Multi-scale
        'overlap_mask': True,                # Overlap mask
        'mask_ratio': 4,                     # Mask ratio
        'dropout': 0.0,                      # Dropout
        'val': True,                         # Val
        'plots': True,                       # Plots
        'save_period': 10,                   # Save period
        'cache': False,                      # Cache
        'rect': False,                       # Rect
        'cos_lr': False,                     # Cos LR
        'close_mosaic': 10,                  # Close mosaic
        'resume': False,                     # Resume
        'amp': True,                         # AMP
        'fraction': 1.0,                     # Fraction
        'profile': False,                    # Profile
        'freeze': None,                      # Freeze
        'multi_scale': False,                # Multi-scale
        'overlap_mask': True,                # Overlap mask
        'mask_ratio': 4,                     # Mask ratio
        'dropout': 0.0,                      # Dropout
        'val': True,                         # Val
        'plots': True,                       # Plots
        'save_period': 10,                   # Save period
        'cache': False,                      # Cache
        'rect': False,                       # Rect
        'cos_lr': False,                     # Cos LR
        'close_mosaic': 10,                  # Close mosaic
        'resume': False,                     # Resume
        'amp': True,                         # AMP
        'fraction': 1.0,                     # Fraction
        'profile': False,                    # Profile
        'freeze': None,                      # Freeze
        'multi_scale': False,                # Multi-scale
        'overlap_mask': True,                # Overlap mask
        'mask_ratio': 4,                     # Mask ratio
        'dropout': 0.0,                      # Dropout
        'val': True,                         # Val
        'plots': True,                       # Plots
        'save_period': 10,                   # Save period
        'cache': False,                      # Cache
        'rect': False,                       # Rect
        'cos_lr': False,                     # Cos LR
        'close_mosaic': 10,                  # Close mosaic
        'resume': False,                     # Resume
        'amp': True,                         # AMP
        'fraction': 1.0,                     # Fraction
        'profile': False,                    # Profile
        'freeze': None,                      # Freeze
        'multi_scale': False,                # Multi-scale
        'overlap_mask': True,                # Overlap mask
        'mask_ratio': 4,                     # Mask ratio
        'dropout': 0.0,                      # Dropout
        'val': True,                         # Val
        'plots': True,                       # Plots
        'save_period': 10,                   # Save period
        'cache': False,                      # Cache
        'rect': False,                       # Rect
        'cos_lr': False,                     # Cos LR
        'close_mosaic': 10,                  # Close mosaic
        'resume': False,                     # Resume
        'amp': True,                         # AMP
        'fraction': 1.0,                     # Fraction
        'profile': False,                    # Profile
        'freeze': None,                      # Freeze
        'multi_scale': False,                # Multi-scale
