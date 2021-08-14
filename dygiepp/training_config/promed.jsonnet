local template = import "template.libsonnet";

template.DyGIE {
  bert_model: "bert-base-cased",
  cuda_device: 0,
  data_paths: {
    train: "data/train.json",
    validation: "data/dev.json",
    test: "data/test.json",
  },
  loss_weights: {
    trigger: 1.0,
    arguments:0.5,
    coref: 0.0,
    events: 1.0
  },
  target_task: "events"
}
