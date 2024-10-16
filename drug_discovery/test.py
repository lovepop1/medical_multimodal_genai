import streamlit as st
from transformers import pipeline, GPT2Tokenizer
from rdkit import Chem
from rdkit.Chem import Draw, Descriptors, rdMolDescriptors
from io import BytesIO

def app():
    # Load the fill-mask pipeline for SMILES completion
    fill_mask = pipeline(
        "fill-mask",
        model='mrm8488/chEMBL_smiles_v1',
        tokenizer='mrm8488/chEMBL_smiles_v1'
    )

    # Load the tokenizer for GPT-2
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    # Set pad_token_id to eos_token_id to handle padding
    tokenizer.pad_token = tokenizer.eos_token

    # Load the text-generation pipeline for generating drug names and usage
    text_gen = pipeline(
        "text-generation",
        model="gpt2",
        tokenizer=tokenizer,
        max_length=100,
        num_return_sequences=1,
        pad_token_id=tokenizer.eos_token_id
    )

    # Function to display molecule from SMILES
    def render_molecule(smile, replace_mask=False):
        if replace_mask:
            smile = smile.replace("<mask>", "*")  # Replace <mask> with wildcard for visualization
        mol = Chem.MolFromSmiles(smile)
        if mol:
            image = Draw.MolToImage(mol, size=(300, 300))
            return image
        else:
            return None

    # Function to get predictions from the model
    def get_predictions(smile):
        predictions = fill_mask(smile)
        return predictions

    # Function to generate drug name and usage
    def generate_drug_info(smile):
        prompt = f"Generate a creative drug name and its usage for the following SMILES notation: {smile}"
        
        # Generate text using max_new_tokens instead of max_length
        generated = text_gen(prompt, max_new_tokens=50, num_return_sequences=1)
        text = generated[0]['generated_text']

        # # Improved parsing to extract name and usage more reliably
        # if "Usage:" in text:
        #     name_part, usage_part = text.split("Usage:")
        #     name = name_part.replace("Drug Name:", "").strip()
        #     usage = usage_part.strip()
        # elif "usage:" in text:
        #     name_part, usage_part = text.split("usage:")
        #     name = name_part.replace("Drug Name:", "").strip()
        #     usage = usage_part.strip()
        # else:
        #     parts = text.split("\n")
        #     name = parts[0].replace("Drug Name:", "").strip() if len(parts) > 0 else "N/A"
        #     usage = "Usage not found."

        # return {"name": name, "usage": usage}
        return text

    # Function to calculate molecular properties (with additional properties)
    def calculate_properties(smile):
        mol = Chem.MolFromSmiles(smile)
        if not mol:
            return {}

        properties = {
            "Molecular Weight": round(Descriptors.MolWt(mol), 2),
            "LogP": round(Descriptors.MolLogP(mol), 2),
            "Number of Hydrogen Donors": Descriptors.NumHDonors(mol),
            "Number of Hydrogen Acceptors": Descriptors.NumHAcceptors(mol),
            "Topological Polar Surface Area (TPSA)": round(Descriptors.TPSA(mol), 2),
            "Number of Rotatable Bonds": Descriptors.NumRotatableBonds(mol),
            "Ring Count": Descriptors.RingCount(mol),
            "Number of Atoms": mol.GetNumAtoms(),
            "Number of Heavy Atoms": Descriptors.HeavyAtomCount(mol),
            "Molecular Formula": rdMolDescriptors.CalcMolFormula(mol),
            "Fraction of SP3 hybridized carbons": round(rdMolDescriptors.CalcFractionCSP3(mol), 2),
            "Number of Heteroatoms": Descriptors.NumHeteroatoms(mol),
            "Valence Electrons": Descriptors.NumValenceElectrons(mol)
        }
        return properties

    # Streamlit App UI
    st.title("💊 MediMolecule")
    st.write("Generate plausible molecular combinations for drug discovery from partial SMILES notations.")

    # Custom CSS for styling
    st.markdown("""
    <style>
    body {
        background-color: #f7f9fc;
    }
    h1 {
        color: #4682B4;
        text-align: center;
    }
    .stTextInput label {
        color: #00008B;
    }
    </style>
    """, unsafe_allow_html=True)

    # Input SMILES string
    st.write("Enter partial SMILES notation with a mask (use <mask>)")
    smile_input = st.text_input(
        "Enter partial SMILES notation with a mask (use <mask>):", 
        placeholder="e.g., CC(C)CN(CC(OP(=O)(O)O)C(Cc1ccccc1)NC(=O)OC1CCOC1)S(=O)(=O)c1ccc(N)<mask>"
    )

    if smile_input:
        # Attempt to parse the input SMILES
        if "<mask>" in smile_input:
            smile_to_validate = smile_input.replace("<mask>", "*")  # Temporarily replace mask for validation
        else:
            smile_to_validate = smile_input

        mol = Chem.MolFromSmiles(smile_to_validate)
        
        if not mol:
            st.error("⚠️ *Invalid SMILES notation. Please check your input and try again.*")
        else:
            with st.spinner('Rendering your input molecule...'):
                # Render the input molecule
                input_mol_img = render_molecule(smile_input, replace_mask=True)
                
                if input_mol_img:
                    st.subheader("🔍 Your Input Molecule:")
                    buf = BytesIO()
                    input_mol_img.save(buf, format="PNG")
                    st.image(buf.getvalue(), caption=smile_input)
                else:
                    st.error("Unable to render the molecule image.")
            
            # Generate and display drug information
            with st.spinner('Generating drug information...'):
                try:
                    drug_info = generate_drug_info(smile_to_validate)
                    properties = calculate_properties(smile_to_validate)
                    
                    st.subheader("📝 Drug Information:")
                    # st.markdown(f"*Name:* {drug_info['name']}")
                    # st.markdown(f"*Usage:* {drug_info['usage']}")
                    st.markdown(drug_info)
                    
                    st.markdown("*Molecular Properties:*")
                    if properties:
                        for prop, value in properties.items():
                            st.write(f"- *{prop}:* {value}")
                    else:
                        st.write("Unable to calculate molecular properties.")
                except Exception as e:
                    st.error(f"An error occurred while generating drug information: {e}")
            
            # Generate molecular combinations
            with st.spinner('Generating molecular combinations...'):
                try:
                    predictions = get_predictions(smile_input)
                    st.subheader("🔮 Top Predicted Molecular Combinations:")
                    
                    for idx, pred in enumerate(predictions, 1):
                        st.markdown(f"*Prediction {idx}:*")
                        st.write(f"*SMILES:* {pred['sequence']}")
                        st.write(f"*Score:* {pred['score']:.4f}")
                        
                        mol_img = render_molecule(pred['sequence'])
                        
                        if mol_img:
                            buf = BytesIO()
                            mol_img.save(buf, format="PNG")
                            st.image(buf.getvalue(), caption=pred['sequence'])
                        else:
                            st.error("Invalid SMILES generated. Skipping visualization.")
                except Exception as e:
                    st.error(f"An error occurred while generating predictions: {e}")

        st.write("*Note*: The generated combinations are hypothetical and should be verified with further testing.")
