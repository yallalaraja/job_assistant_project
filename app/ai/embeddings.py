from sentence_transformers import SentenceTransformer


model = None
model_load_error = None


def get_model():

    global model, model_load_error

    if model_load_error is not None:

        raise model_load_error

    if model is None:

        try:

            model = SentenceTransformer(
                "all-MiniLM-L6-v2"
            )

        except Exception as exc:

            model_load_error = exc

            raise

    return model


def generate_embedding(text: str):

    if not text:
        text = ""

    return get_model().encode(text)
