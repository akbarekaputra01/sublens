import pickle
import numpy as np

# Load the dataset
with open('dataASL.pickle', 'rb') as f:
    dataset = pickle.load(f)

data = dataset['data']
labels = dataset['labels']

print(f"Dataset loaded successfully!")
print(f"Total samples: {len(data)}")
print(f"Total labels: {len(labels)}")

# Check data structure
if len(data) > 0:
    print(f"Sample data shape: {len(data[0])} features")
    print(f"First sample features: {len(data[0])}")
    print(f"Data type: {type(data[0])}")

# Show unique labels and their counts
unique_labels = set(labels)
print(f"\nUnique labels: {sorted(unique_labels)}")
print(f"Number of unique classes: {len(unique_labels)}")

# Count samples per class
from collections import Counter
label_counts = Counter(labels)
print("\nSamples per class:")
for label in sorted(unique_labels):
    print(f"  {label}: {label_counts[label]} samples")

# Show some statistics about feature lengths
if len(data) > 0:
    feature_lengths = [len(sample) for sample in data]
    print(f"\nFeature length statistics:")
    print(f"  Min features: {min(feature_lengths)}")
    print(f"  Max features: {max(feature_lengths)}")
    print(f"  Mean features: {np.mean(feature_lengths):.2f}")
    print(f"  Std features: {np.std(feature_lengths):.2f}")
    
    # Check if all samples have the same number of features
    if len(set(feature_lengths)) == 1:
        print(f"  All samples have the same number of features: {feature_lengths[0]}")
    else:
        print(f"  Warning: Samples have different numbers of features!")
        print(f"  Unique feature counts: {sorted(set(feature_lengths))}") 