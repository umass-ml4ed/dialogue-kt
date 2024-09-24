import argparse

from annotate import annotate
from human_eval import human_eval
from training import train, test, BASELINE_MODELS
from visualize import visualize
from utils import initialize_seeds, bool_type

def main():
    initialize_seeds(221)

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_annotate = subparsers.add_parser("annotate", help="Annotate dialogues")
    parser_annotate.set_defaults(func=annotate)
    parser_annotate.add_argument("--mode", type=str, choices=["collect", "analyze"], help="Collect annotations or analyze existing files")
    parser_annotate.add_argument("--use_azure", action="store_true", help="Use Azure endpoint")
    parser_annotate.add_argument("--openai_model", type=str, help="Model identifier string")

    parser_hum_eval = subparsers.add_parser("human-eval", help="Create/analyze human evaluation files")
    parser_hum_eval.set_defaults(func=human_eval)
    parser_hum_eval.add_argument("--mode", type=str, choices=["create", "analyze"], help="Create evaluation files or analyze existing files")

    parser_train = subparsers.add_parser("train", help="Train KT model")
    parser_train.set_defaults(func=train)
    parser_train.add_argument("--epochs", type=int, help="Number of training epochs")
    parser_train.add_argument("--lr", type=float, help="Learning rate")
    parser_train.add_argument("--wd", type=float, help="Weight decay")
    parser_train.add_argument("--gc", type=float, help="Gradient clipping norm")
    parser_train.add_argument("--grad_accum_steps", type=int, help="Steps to accumulate gradients for")
    parser_train.add_argument("--r", type=int, help="LoRA rank")
    parser_train.add_argument("--lora_alpha", type=int, help="LoRA alpha")
    parser_train.add_argument("--optim", type=str, choices=["adamw", "adafactor"], default="adamw", help="Optimizer")
    parser_train.add_argument("--pt_model_name", type=str, help="Name of pre-trained model to initialize weights from")
    parser_train.add_argument("--hyperparam_sweep", action="store_true", help="Run a hyperparameter sweep experiment")

    parser_test = subparsers.add_parser("test", help="Test KT model")
    parser_test.set_defaults(func=test)

    parser_visualize = subparsers.add_parser("visualize", help="Visualize KCs")
    parser_visualize.set_defaults(func=visualize)

    for subparser in [parser_annotate, parser_hum_eval, parser_train, parser_test, parser_visualize]:
        subparser.add_argument("--dataset", type=str, choices=["comta", "mathdial"], default="comta", help="Which dataset to use")
        subparser.add_argument("--split_by_subject", action="store_true", help="For CoMTA, define train/test and folds using subjects")
        subparser.add_argument("--typical_cutoff", type=int, default=1, help="For MathDial, lowest acceptable dialogue 'typical' score")
        subparser.add_argument("--tag_src", type=str, choices=["base", "atc"], default="atc", help="Source of KC tags - base: generated by LLM, atc: ATC standards")
        subparser.add_argument("--debug", action="store_true", help="Use subset of data for debugging")

    for subparser in [parser_train, parser_test, parser_visualize]:
        subparser.add_argument("--model_type", type=str, choices=["lmkt", "random", "majority", "bkt"] + BASELINE_MODELS, default="lmkt", help="Model architecture to use")
        subparser.add_argument("--model_name", type=str, help="Name of model to save for training or load for testing")
        subparser.add_argument("--base_model", type=str, default="meta-llama/Meta-Llama-3.1-8B-Instruct", help="HuggingFace base model for LLMKT")
        subparser.add_argument("--inc_first_label", action="store_true", help="Include first turn label in dialogues when testing")

    for subparser in [parser_train, parser_test]:
        subparser.add_argument("--batch_size", type=int, help="Model batch size")
        subparser.add_argument("--crossval", action="store_true", help="Run training/testing over all folds and aggregate results")
        subparser.add_argument("--testonval", action="store_true", help="Run testing phase on validation set (automatic for hyperparam_sweep)")
        subparser.add_argument("--pack_kcs", type=bool_type, default=True, help="For LLMKT, pack all KCs for a turn in a single prompt")
        subparser.add_argument("--quantize", type=bool_type, default=False, help="Quantize LLMKT base model")
        subparser.add_argument("--prompt_inc_labels", type=bool_type, default=False, help="For LLMKT, include explicit correctness and KC labels in prompt")
        subparser.add_argument("--emb_size", type=int, help="Latent state dimension for DKT family models")

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
