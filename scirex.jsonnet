
local template = import "template.libsonnet";

template.DyGIE {
  bert_model: "bert-base-cased",
  cuda_device: 0,
  data_paths: {
    train: "data/scirex/train.json",
    validation: "data/scirex/dev.json",
    test: "data/scirex/test.json",
  },
  loss_weights: {
    ner: 1.0,
    relation:0.0,
    coref: 0.0,
    events: 0.0
  },
  trainer +: {
    num_epochs: 19
  },
  target_task: "ner"
}
