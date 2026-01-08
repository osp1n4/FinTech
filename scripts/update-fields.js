db = db.getSiblingDB('fraud_detection');

// Actualizar documentos con risk_level y status según risk_score
db.evaluations.updateMany(
  { risk_score: { $lte: 0.3 } },
  { $set: { risk_level: "LOW_RISK", status: "approved" } }
);

db.evaluations.updateMany(
  { risk_score: { $gt: 0.3, $lte: 0.7 } },
  { $set: { risk_level: "MEDIUM_RISK", status: "pending" } }
);

db.evaluations.updateMany(
  { risk_score: { $gt: 0.7 } },
  { $set: { risk_level: "HIGH_RISK", status: "rejected" } }
);

print("Documentos actualizados exitosamente!");
print("Total: " + db.evaluations.countDocuments());
