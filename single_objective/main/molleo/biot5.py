from transformers import T5Tokenizer, T5ForConditionalGeneration
import selfies as sf
from rdkit import Chem
from main.molleo.mol_lm_utils import clean_edits

class BioT5:
    def __init__(self):

        self.tokenizer = T5Tokenizer.from_pretrained("QizhiPei/biot5-base-text2mol")
        self.model = T5ForConditionalGeneration.from_pretrained('QizhiPei/biot5-base-text2mol')

        self.task2description = {
                'qed': 'Definition: You are given a molecule SELFIES. Your job is to generate a SELFIES molecule that looks more like a drug.\n\n',
                'jnk3': 'Definition: You are given a molecule SELFIES. Your job is to generate a SELFIES molecule that is a greater inhibitor of JNK3.\n\n',
                'drd2': 'Definition: You are given a molecule SELFIES. Your job is to generate a SELFIES molecule that inhibits DRD2 more.\n\n',
                'gsk3b': 'Definition: You are given a molecule SELFIES. Your job is to generate a SELFIES molecule that inhibits GSK3B more.\n\n',
                'Isomers_C9H10N2O2PF2Cl': 'Definition: You are given a molecule SELFIES. Your job is to generate a SELFIES molecule that has the formula C9H10N2O2PF2Cl.\n\n',
                'perindopril_mpo': 'Definition: You are given a molecule SELFIES. Your job is to generate a SELFIES molecule that looks more like Perindopril.\n\n',
                'sitagliptin_mpo': 'Definition: You are given a molecule SELFIES. Your job is to generate a SELFIES molecule that looks more like Sitagliptin.\n\n',
                'ranolazine_mpo': 'Definition: You are given a molecule SELFIES. Your job is to generate a SELFIES molecule that looks more like Ranolazine.\n\n',
                'thiothixene_rediscovery': 'Definition: You are given a molecule SELFIES. Your job is to generate a SELFIES molecule that looks more like Thiothixene.\n\n',
                'mestranol_similarity': 'Definition: You are given a molecule SELFIES. Your job is to generate a SELFIES molecule that looks more like Mestranol.\n\n',
                }
        self.task=None

    def edit(self, smiles_list):
        task = self.task
        task_definition = self.task2description[task[0]]

        editted_molecules = []
        for i, MOL in enumerate(smiles_list):
            SMILES = Chem.MolToSmiles(MOL)

            print("===== for SMILES {} =====".format(SMILES))
            try:
                selfies_input = sf.encoder(SMILES)
            except:
                print("could not encode input smiles", SMILES)
                editted_molecules.append(None)
                continue
            task_input = f'Now complete the following example -\nInput: <bom>{selfies_input}<eom>\nOutput: '

            model_input = task_definition + task_input
            if i == 0:
                print("sample model input", model_input)
            input_ids = self.tokenizer(model_input, return_tensors="pt").input_ids
            
            generation_config = self.model.generation_config
            generation_config.max_length = 512
            generation_config.num_beams = 1
            
            outputs = self.model.generate(input_ids, generation_config=generation_config)
            output_selfies = self.tokenizer.decode(outputs[0], skip_special_tokens=True).replace(' ', '')
            print("output selfies", output_selfies)
            
            try:
                output_smiles = sf.decoder(output_selfies)
                print("generated smiles", output_smiles)
                mol = Chem.MolFromSmiles(output_smiles)
                editted_molecules.append(mol)
                print("added!")

            except:
                pass
        return editted_molecules
if __name__ == "__main__":
    model = BioT5()
    print(model.edit(["CC(O)CC(=O)C(=O)[O-1]"]))

