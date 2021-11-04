augs_num = 5
augs_epoch = 20

augs = [
    dict(
        type='CLAHE',
        p=1.0),
    dict(
        type='RandomGamma',
        p=1.0),
    dict(
        type='HueSaturationValue',
        p=1.0),
    dict(
        type='ChannelDropout',
        p=1.0),
    dict(
        type='ChannelShuffle',
        p=1.0),
    dict(
        type='RGBShift',
        p=1.0),

    
    dict(
        type='ShiftScaleRotate',
        p=1.0),
    dict(
        type='RandomRotate90',
        p=1.0),

    
    dict(
        type='PiecewiseAffine',
        p=1.0),
    dict(
        type='CoarseDropout',
        max_height=8,
        max_width=8,
        p=1.0),
    dict(
        type='ElasticTransform',
        border_mode=0,
        p=1.0),
    dict(
        type='ElasticTransform',
        p=1.0),
    dict(
        type='GridDistortion',
        border_mode=0,
        p=1.0
    ),
    dict(
        type='RandomCrop',
        height=300,
        width=300,
        p=1.0),
    dict(
        type='OpticalDistortion',
        distort_limit=0.5,
        p=1.0)
    ]

alb_transform = [
    dict(
        type='VerticalFlip',
        p=0.3),
    dict(
        type='HorizontalFlip',
        p=0.3),
    dict(
        type='OneOf',
        transforms=[
            dict(
                type='GaussNoise',
                p=1.0),
            dict(
                type='GaussianBlur',
                p=1.0),
            dict(
                type='Blur',
                p=1.0)
        ],
        p=0.3),
    dict(
        type='OneOf',
        # transforms=augs,
        transforms=[
            augs[augs_num]
        ],
        p=0.3
    )
    
]

# dataset settings
# dataset_type = 'COCOStuffDataset'
dataset_type = 'CustomDataset'
data_root = '/opt/ml/segmentation/input/mmseg/'

# class settings
classes = ['Background', 'General trash', 'Paper', 'Paper pack', 'Metal', 'Glass', 'Plastic','Styrofoam', 'Plastic bag', 'Battery', 'Clothing']
palette = [
    [0, 0, 0],
    [192, 0, 128], [0, 128, 192], [0, 128, 64],
    [128, 0, 0], [64, 0, 128], [64, 0, 192],
    [192, 128, 64], [192, 192, 128], [64, 64, 128], [128, 0, 192]
    ]

# set normalize value
img_norm_cfg = dict(
    mean=[117.551, 112.259, 106.825], std=[59.866, 58.944, 62.162], to_rgb=True)
    # mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True)
crop_size = (512, 512)
train_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(type='LoadAnnotations'),
    dict(type='Resize', img_scale=(512, 512)),
    # dict(type='Resize', img_scale=(512, 512), ratio_range=(0.5, 2.0)),
    dict(
        type='Albu',
        transforms=alb_transform,
    ),
    dict(type='RandomFlip', prob=0.3),
    # dict(type='RandomRotate', prob=0.3, degree=45),
    # dict(type='PhotoMetricDistortion'),
    dict(type='Normalize', **img_norm_cfg),
    dict(type='Pad', size=crop_size, pad_val=0, seg_pad_val=255),
    dict(type='DefaultFormatBundle'),
    dict(type='Collect', keys=['img', 'gt_semantic_seg']),
]
val_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(
        type='MultiScaleFlipAug',
        img_scale=(512, 512),
        # img_ratios=[0.5, 0.75, 1.0, 1.25, 1.5, 1.75],
        flip=False,
        transforms=[
            dict(type='Resize', img_scale=(512,512), keep_ratio=True),
            dict(type='RandomFlip'),
            dict(type='Normalize', **img_norm_cfg),
            dict(type='ImageToTensor', keys=['img']),
            dict(type='Collect', keys=['img', 'gt_semantic_seg']),
        ])
]
test_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(
        type='MultiScaleFlipAug',
        img_scale=(512, 512),
        # img_ratios=[0.5, 0.75, 1.0, 1.25, 1.5, 1.75],
        flip=False,
        transforms=[
            dict(type='Resize', img_scale=(512,512), keep_ratio=True),
            # dict(type='Resize', keep_ratio=True),
            # dict(type='RandomFlip'),
            dict(type='Normalize', **img_norm_cfg),
            dict(type='ImageToTensor', keys=['img']),
            dict(type='Collect', keys=['img']),
        ])
]
data = dict(
    samples_per_gpu=16,
    workers_per_gpu=8,
    train=dict(
        classes=classes,
        palette=palette,
        type=dataset_type,
        reduce_zero_label=False, 
        img_dir=data_root + "images/training",
        ann_dir=data_root + "annotations/training",
        pipeline=train_pipeline),
    val=dict(
        classes=classes,
        palette=palette,
        type=dataset_type,
        reduce_zero_label=False,
        img_dir=data_root + "images/validation",
        ann_dir=data_root + "annotations/validation",
        pipeline=test_pipeline),
    test=dict(
        classes=classes,
        palette=palette,
        type=dataset_type,
        reduce_zero_label=False,
        img_dir=data_root + "test",
        pipeline=test_pipeline))


###########################################################################
#Schedule
###########################################################################
lr = 1e-4  # max learning rate
optimizer = dict(type='AdamW', lr=lr, weight_decay=0.01)
optimizer_config = dict(grad_clip=dict(max_norm=10, norm_type=2))
lr_config = dict(
    policy='CosineAnnealing',
    warmup='linear',
    warmup_iters=300,
    warmup_ratio=1.0 / 10,
    min_lr_ratio=7e-6)
# runtime settings
total_epochs = augs_epoch


###########################################################################
#Runtime
###########################################################################

expr_name = f'{augs_num}_{augs[augs_num]["type"]}'

dist_params = dict(backend='nccl')

runner = dict(type='EpochBasedRunner', max_epochs=augs_epoch)
checkpoint_config = dict(interval=20)
log_config = dict(
    interval=10,
    hooks=[
        dict(type='TextLoggerHook'),  
        dict(
            type='WandbLoggerHook',
            init_kwargs=dict(
                project='segm_augs',
                name=expr_name,
                entity='ark10806'
        ))
    ])
custom_hooks = [dict(type='NumClassCheckHook')]
dist_params = dict(backend='nccl')
log_level = 'INFO'
load_from = None
resume_from = None
workflow = [('train', 1)]
evaluation = dict(metric='mIoU', pre_eval=True,save_best='mIoU')
work_dir = './work_dirs/' + expr_name
gpu_ids = range(0, 1)


###########################################################################
#Model
###########################################################################
# model settings
norm_cfg = dict(type='SyncBN', requires_grad=True)
backbone_norm_cfg = dict(type='LN', requires_grad=True)


model = dict(
    type='EncoderDecoder',
    pretrained='/opt/ml/segmentation/mmsegmentation/configs/_base_/models/UperSwin/pretrained/Converted_upernet_swin_tiny_patch4_window7_512x512_160k_ade20k_pretrain_224x224_1K_20210531_112542-e380ad3e.pth',
    backbone=dict(
        type='SwinTransformer',
        pretrain_img_size=224,
        embed_dims=96,
        patch_size=4,
        window_size=7,
        mlp_ratio=4,
        depths=[2, 2, 6, 2],
        num_heads=[3,6,12,24],
        strides=(4, 2, 2, 2),
        out_indices=(0, 1, 2, 3),
        qkv_bias=True,
        qk_scale=None,
        patch_norm=True,
        drop_rate=0.,
        attn_drop_rate=0.,
        drop_path_rate=0.3,
        use_abs_pos_embed=False,
        act_cfg=dict(type='GELU'),
        norm_cfg=backbone_norm_cfg,
        # init_cfg=dict(type='Pretrained', checkpoint='/opt/ml/segmentation/mmsegmentation/configs/swin/upernet_swin_base_patch4_window7_512x512.pth'),
        ),
    decode_head=dict(
        type='UPerHead',
        in_channels=[96, 96*2, 96*4, 96*8],
        in_index=[0, 1, 2, 3],
        pool_scales=(1, 2, 3, 6),
        channels=512,
        dropout_ratio=0.1,
        num_classes=11,
        norm_cfg=norm_cfg,
        align_corners=False,
        loss_decode=dict(
            type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0)),
    auxiliary_head=dict(
        type='FCNHead',
        in_channels=384,
        in_index=2,
        channels=256,
        num_convs=1,
        concat_input=False,
        dropout_ratio=0.1,
        num_classes=11,
        norm_cfg=norm_cfg,
        align_corners=False,
        loss_decode=dict(
            type='CrossEntropyLoss', use_sigmoid=False, loss_weight=0.4)),
    # model training and testing settings
    train_cfg=dict(),
    test_cfg=dict(mode='whole'))