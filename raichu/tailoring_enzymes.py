from enum import Enum, unique
from raichu.reactions.general_tailoring_reactions import proteolytic_cleavage, find_atoms_for_tailoring, remove_atom, single_bond_oxidation, addition, oxidative_bond_formation, epoxidation, double_bond_reduction, double_bond_shift, macrolactam_formation, cyclodehydration
from raichu.data.attributes import PRENYL_TRANSFERASE_SUBSTRATES_TO_SMILES
from raichu.data.molecular_moieties import CO_BOND, CC_DOUBLE_BOND, PEPTIDE_BOND, CC_SINGLE_BOND, KETO_GROUP, C_CARBOXYL, ASPARTIC_ACID, GLUTAMIC_ACID, CYSTEINE, SERINE, THREONINE
from pikachu.reactions.functional_groups import find_atoms, find_bonds, combine_structures, GroupDefiner
@unique
class TailoringEnzymeType(Enum):
    METHYLTRANSFERASE = 1
    C_METHYLTRANSFERASE = 2
    N_METHYLTRANSFERASE = 3
    O_METHYLTRANSFERASE = 4
    HYDROXYLATION = 5
    OXIDATIVE_BOND_FORMATION = 6
    EPOXIDATION = 7
    DOUBLE_BOND_REDUCTION = 8
    DOUBLE_BOND_SHIFT = 9
    PRENYLTRANSFERASE = 10
    ACETYLTRANSFERASE = 11
    ACYLTRANSFERASE = 12
    AMINOTRANSFERASE = 13
    DOUBLE_BOND_FORMATION = 14
    KETO_REDUCTION = 15
    ALCOHOLE_DEHYDROGENASE = 16
    DEHYDRATASE = 17
    DECARBOXYLASE = 18
    MONOAMINE_OXIDASE = 19
    HALOGENASE = 20
    PEPTIDASE = 21
    PROTEASE = 22
    MACROLACTAM_SYNTHETASE = 23
    CYCLODEHYDRATION = 24

    
    
    @staticmethod
    def from_string(label: str) -> "TailoringEnzymeType":
        for value in TailoringEnzymeType:
            if str(value.name) == label:
                return value
        raise ValueError(f"Unknown tailoring enzyme: {label}")


class TailoringEnzyme:

    def __init__(self, gene_name, enzyme_type, modification_sites:list = None, substrate:str = None) -> None:
        self.gene_name = gene_name
        self.type = TailoringEnzymeType.from_string(enzyme_type)
        self.modification_sites = modification_sites
        self.substrate = substrate

    def do_tailoring(self, structure):
        """
        Performs tailoring reaction
        """
        if len(self.modification_sites)==0:
            return structure
        if self.type.name == "HYDROXYLATION":
            for atom in self.modification_sites:
                if len(atom) == 0:
                    continue
                atom = atom[0] #only one atom is hydroxylated at a time
                atom = structure.get_atom(atom)
                structure = addition(atom, "O", structure)
        elif self.type.name in ["METHYLTRANSFERASE", "C_METHYLTRANSFERASE", "N_METHYLTRANSFERASE", "O_METHYLTRANSFERASE"]:
            for atom in self.modification_sites:
                if len(atom) == 0:
                    continue
                atom = atom[0] #only one atom is methylated at a time
                atom = structure.get_atom(atom)
                structure = addition(atom, "C", structure)
        elif self.type.name == "PRENYLTRANSFERASE":
            for atom in self.modification_sites:
                if len(atom) == 0:
                    continue
                atom = atom[0]  # only one atom is methylated at a time
                atom = structure.get_atom(atom)
                if self.substrate not in PRENYL_TRANSFERASE_SUBSTRATES_TO_SMILES:
                    raise ValueError(
                        f"Not implemented prenyltransferase substrate: {self.substrate}")
                substrate = PRENYL_TRANSFERASE_SUBSTRATES_TO_SMILES[self.substrate]
                structure = addition(
                    atom, substrate, structure)
        elif self.type.name == "ACETYLTRANSFERASE":
            for atom in self.modification_sites:
                if len(atom) == 0:
                    continue
                atom = atom[0]  # only one atom is methylated at a time
                atom = structure.get_atom(atom)
                structure = addition(atom, "[H]C(C)=O", structure)
        elif self.type.name == "ACYLTRANSFERASE":
            for atom in self.modification_sites:
                if len(atom) == 0:
                    continue
                atom = atom[0]  # only one atom is methylated at a time
                atom = structure.get_atom(atom)
                if self.substrate:
                    structure = addition(atom, self.substrate, structure)
        elif self.type.name == "OXIDATIVE_BOND_FORMATION":
            for atoms in self.modification_sites:
                if len(atoms) < 2:
                    continue
                atom1 = structure.get_atom(atoms[0])
                atom2 = structure.get_atom(atoms[1])
                structure = oxidative_bond_formation(atom1, atom2, structure)
        elif self.type.name == "EPOXIDATION":
            for atoms in self.modification_sites:
                if len(atoms) < 2:
                    continue
                atom1 = structure.get_atom(atoms[0])
                atom2 = structure.get_atom(atoms[1])
                structure = epoxidation(atom1, atom2, structure)
        elif self.type.name == "DOUBLE_BOND_REDUCTION":
            for atoms in self.modification_sites:
                if len(atoms) < 2:
                    continue
                atom1 = structure.get_atom(atoms[0])
                atom2 = structure.get_atom(atoms[1])
                structure = double_bond_reduction(atom1, atom2, structure)
        elif self.type.name == "DOUBLE_BOND_FORMATION":
            for atoms in self.modification_sites:
                if len(atoms) < 2:
                    continue
                atom1 = structure.get_atom(atoms[0])
                atom2 = structure.get_atom(atoms[1])
                structure = single_bond_oxidation(atom1, atom2, structure)
        elif self.type.name == "DOUBLE_BOND_SHIFT":
            for atoms in self.modification_sites:
                if len(atoms) < 4:
                    continue
                old_double_bond_atom1 = structure.get_atom(atoms[0])
                old_double_bond_atom2 = structure.get_atom(atoms[1])
                new_double_bond_atom1 = structure.get_atom(atoms[2])
                new_double_bond_atom2 = structure.get_atom(atoms[3])
                structure = double_bond_shift(
                    structure, old_double_bond_atom1, old_double_bond_atom2, new_double_bond_atom1, new_double_bond_atom2)
        elif self.type.name == "AMINOTRANSFERASE":
            for atom in self.modification_sites:
                if len(atom) == 0:
                    continue
                atom1 = atom[0] #only one atom is modified at a time
                atom1 = structure.get_atom(atom1)
                oxygen = atom1.get_neighbour('O')
                structure = double_bond_reduction(atom1, oxygen, structure)
                oxygen = structure.get_atom(oxygen)
                structure = remove_atom(oxygen, structure)
                atom = structure.get_atom(atom)
                structure = addition(atom, "N", structure)
        elif self.type.name == "KETO_REDUCTION":
            for atom in self.modification_sites:
                if len(atom) == 0:
                    continue
                atom1 = atom[0] #only one atom is modified at a time
                atom1 = structure.get_atom(atom1)
                if atom1.type != "O":
                    raise ValueError(f"Can not perform KETO_REDUCTION on atom {atom1}, since there is no oxygen to be reduced.")
                atom2 = atom1.get_neighbour('C')
                structure = double_bond_reduction(atom1, atom2, structure)
        elif self.type.name == "ALCOHOLE_DEHYDROGENASE":
            for atom in self.modification_sites:
                if len(atom) == 0:
                    continue
                atom1 = atom[0] #only one atom is modified at a time
                atom1 = structure.get_atom(atom1)
                if atom1.type != "O":
                    raise ValueError(f"Can not perform ALCOHOLE_DEHYDROGENASE on atom {atom1}, since there is no oxygen to be reduced.")
                atom2 = atom1.get_neighbour('C')
                structure = single_bond_oxidation(atom1, atom2, structure)
        elif self.type.name == "DECARBOXYLASE":
            for atom in self.modification_sites:
                if len(atom) == 0:
                    continue
                atom1 = atom[0] #only one atom is modified at a time
                atom1 = structure.get_atom(atom1)
                structure = remove_atom(atom1, structure)     
        elif self.type.name == "DEHYDRATASE":
            for atoms in self.modification_sites:
                if len(atoms) < 2:
                    continue
                atom1 = structure.get_atom(atoms[0])
                atom2 = structure.get_atom(atoms[1])
                oxygen = atom1.get_neighbour('O')
                if not oxygen:
                    oxygen = atom2.get_neighbour('O')
                if not oxygen:
                    raise ValueError(f"Can not perform DEHYDRATASE on atoms {atom1} and {atom2}, since there is no hydroxygroup to be removed.")
                structure = remove_atom(oxygen, structure)
                structure = single_bond_oxidation(atom1, atom2, structure)
        elif self.type.name == "MONOAMINE_OXYDASE":
            for atom in self.modification_sites:
                if len(atom) == 0:
                    continue
                atom1 = atom[0] #only one atom is modified at a time
                atom1 = structure.get_atom(atom1)
                if atom1.type != "N":
                    raise ValueError(f"Can not perform MONOAMINE_OXYDASE on atom {atom1}, since there is no nitrogen to be removed.")
                structure = remove_atom(atom1, structure) 
        elif self.type.name == "HALOGENASE":
            for atom in self.modification_sites:
                if len(atom) == 0:
                    continue
                atom1 = atom[0]  # only one atom is modified at a time
                atom1 = structure.get_atom(atom1)
                if self.substrate in ["F", "Cl", "Br", "I"]:
                    structure = addition(atom1, self.substrate, structure)
        elif self.type.name in ["PROTEASE", "PEPTIDASE"]:
            for atoms in self.modification_sites:
                if len(atoms) != 2:
                    continue
                atom1 = structure.get_atom(atoms[0])
                atom2 = structure.get_atom(atoms[1])
                structure = proteolytic_cleavage(atom1.get_bond(atom2), structure)
        elif self.type.name == "MACROLACTAM_SYNTHETASE":
            for atom in self.modification_sites:
                if len(atom) == 0:
                    continue
                atom1 = atom[0]  # only one atom is modified at a time
                atom1 = structure.get_atom(atom1)
                structure = macrolactam_formation(structure, atom1)
        elif self.type.name == "CYCLODEHYDRATION":
            for atom in self.modification_sites:
                if len(atom) == 0:
                    continue
                atom1 = atom[0]  # only one atom is modified at a time
                atom1 = structure.get_atom(atom1)
                break_all = False
                for neighbour_1 in atom1.neighbours:
                    if neighbour_1.type == "C":
                        for neighbour_2 in neighbour_1.neighbours:
                          if neighbour_2.type == "C":
                                nitrogen = neighbour_2.get_neighbour("N")
                                if nitrogen:
                                    carbon = nitrogen.get_neighbour("C")
                                    oxygen = carbon.get_neighbour("O")
                                    if carbon and nitrogen:
                                        structure = cyclodehydration(
                                            structure, atom1, oxygen)
                                        # breaking out of all loops
                                        break_all = True
                                        break
                        if break_all:
                            break
                else:
                    raise ValueError(
                        f"Can not perform CYCLODEHYDRATION on atom {atom1}, since there is downstream amino acid.")
        return structure




    
    def get_possible_sites(self, structure):
        possible_sites = []
        if self.type.name in ["HYDROXYLATION",]:
           possible_sites.extend(find_atoms_for_tailoring(structure, "C"))
        elif self.type.name in ["C_METHYLTRANSFERASE", "N_METHYLTRANSFERASE", "O_METHYLTRANSFERASE"]:
                atom = self.type.name.split("_")[0]
                possible_sites.extend(find_atoms_for_tailoring(structure, atom))
        elif self.type.name in ["METHYLTRANSFERASE", "PRENYLTRANSFERASE", "ACETYLTRANSFERASE", "ACYLTRANSFERASE", "OXIDATIVE_BOND_FORMATION", "HALOGENASE"]:
            possible_sites.extend(
                find_atoms_for_tailoring(structure, "C"))
            possible_sites.extend(
                find_atoms_for_tailoring(structure, "N"))
            possible_sites.extend(
                find_atoms_for_tailoring(structure, "O"))
            possible_sites.extend(
                find_atoms_for_tailoring(structure, "S"))
        
        elif self.type.name in ["EPOXIDATION", "DOUBLE_BOND_REDUCTION"]:
            peptide_bonds = find_bonds(
                CC_DOUBLE_BOND, structure)
            for bond in peptide_bonds:
                possible_sites.append(bond.neighbours)
        
        elif self.type.name == "DOUBLE_BOND_FORMATION":
            peptide_bonds = find_bonds(
                CC_SINGLE_BOND, structure)
            for bond in peptide_bonds:
                possible_sites.append(bond.neighbours)

        elif self.type.name == "DOUBLE_BOND_SHIFT":
            peptide_bonds = find_bonds(
                CC_DOUBLE_BOND, structure)
            for bond in peptide_bonds:
                neighbouring_bonds = bond.get_neighbouring_bonds()
                for neighbouring_bond in neighbouring_bonds:
                    if not "H" in [atom.type for atom in neighbouring_bond.neighbours]:
                        possible_sites.append(
                            bond.neighbours+neighbouring_bond.neighbours)

        elif self.type.name == "AMINOTRANSFERASE":
            possible_sites.extend(find_atoms(KETO_GROUP, structure))

        elif self.type.name == "KETO_REDUCTION":
            oxygens = find_atoms(KETO_GROUP, structure)
            possible_sites.extend([oxygen.get_neighbour("O") for oxygen in oxygens])
        
        elif self.type.name == "ALCOHOLE_DEHYDROGENASE":
            possible_sites.extend(
                find_atoms_for_tailoring(structure, "O"))
        
        elif self.type.name == "DECARBOXYLASE":
            possible_sites.extend(find_atoms(C_CARBOXYL, structure))
        
        elif self.type.name == "DEHYDRATASE":
            co_bonds = find_bonds(CO_BOND, structure)
            for co_bond in co_bonds:
                neighbouring_bonds = co_bond.get_neighbouring_bonds()
                for neighbouring_bond in neighbouring_bonds:
                    if not "H" in [atom.type for atom in neighbouring_bond.neighbours] and neighbouring_bond.type == "single":
                        for neighbouring_atom in neighbouring_bond.neighbours:
                            if neighbouring_atom != co_bond.get_neighbour("C") and neighbouring_atom.has_neighbour("H"):
                                possible_sites.append(neighbouring_bond.neighbours)
    
        elif self.type.name == "MONOAMINE_OXIDASE":
            n_atoms_with_one_h = find_atoms_for_tailoring(structure, "N")
            for n_atom in n_atoms_with_one_h:
                if [atom.type for atom in n_atom.neighbours].count("H") == 2:
                    possible_sites.append(n_atom)
        
        elif self.type.name in ["PROTEASE", "PEPTIDASE"]:
            peptide_bonds = find_bonds(
                PEPTIDE_BOND, structure)
            for bond in peptide_bonds:
                possible_sites.append(bond.neighbours)
        elif self.type.name == "MACROLACTAM_SYNTHETASE":
            asp_glu_oxygen = find_atoms(
                ASPARTIC_ACID, structure) + find_atoms(GLUTAMIC_ACID, structure)
            possible_sites.append(asp_glu_oxygen)
        elif self.type.name == "CYCLODEHYDRATION":
            cys_ser_thr_x = find_atoms(
                CYSTEINE, structure) + find_atoms(SERINE, structure) + find_atoms(THREONINE, structure)
            possible_sites.append(cys_ser_thr_x)
        return possible_sites
