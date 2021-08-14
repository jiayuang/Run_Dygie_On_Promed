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
    ner: 1.0,
    relation:0.0,
    coref: 0.0,
    events: 0.0
  },
  target_task: "ner"
}
