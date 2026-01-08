// Script para actualizar los reasons con los códigos correctos
db = db.getSiblingDB('fraud_detection');

// Transacciones normales (LOW_RISK) - sin reasons específicos
db.evaluations.updateMany(
  { risk_level: "LOW_RISK" },
  { $set: { reasons: [] } }
);

// Transacciones con riesgo medio (MEDIUM_RISK)
db.evaluations.updateMany(
  { risk_level: "MEDIUM_RISK" },
  { $set: { reasons: ["unusual_location"] } }
);

// Transacciones de alto riesgo (HIGH_RISK)
db.evaluations.updateMany(
  { risk_level: "HIGH_RISK" },
  { $set: { reasons: ["amount_threshold_exceeded"] } }
);

print("Reasons actualizados correctamente!");
print("Total documentos: " + db.evaluations.countDocuments());
