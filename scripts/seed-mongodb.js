// Script para insertar datos de prueba directamente en MongoDB

db = db.getSiblingDB('fraud_detection');

// Limpiar colecciones existentes
db.fraud_evaluations.deleteMany({});
db.evaluations.deleteMany({});
db.audit_logs.deleteMany({});

print("Insertando datos de prueba...");

// Insertar evaluaciones de fraude
const evaluations = [
    {
        transaction_id: "txn-10001",
        user_id: "Paula05",
        amount: 450.75,
        timestamp: new Date("2026-01-08T10:15:00Z"),
        merchant: "Amazon Store",
        is_fraudulent: false,
        risk_score: 0.15,
        decision: "approved",
        reasons: ["Monto normal", "Ubicación esperada"],
        evaluated_at: new Date()
    },
    {
        transaction_id: "txn-10002",
        user_id: "John99",
        amount: 2500.00,
        timestamp: new Date("2026-01-08T10:20:00Z"),
        merchant: "Electronics Plus",
        is_fraudulent: true,
        risk_score: 0.85,
        decision: "rejected",
        reasons: ["Monto excede umbral", "Ubicación sospechosa"],
        evaluated_at: new Date()
    },
    {
        transaction_id: "txn-10003",
        user_id: "Maria123",
        amount: 125.50,
        timestamp: new Date("2026-01-08T10:25:00Z"),
        merchant: "Coffee Shop",
        is_fraudulent: false,
        risk_score: 0.05,
        decision: "approved",
        reasons: ["Transacción normal"],
        evaluated_at: new Date()
    },
    {
        transaction_id: "txn-10004",
        user_id: "Paula05",
        amount: 1800.00,
        timestamp: new Date("2026-01-08T10:30:00Z"),
        merchant: "Jewelry Store",
        is_fraudulent: true,
        risk_score: 0.75,
        decision: "manual_review",
        reasons: ["Monto alto", "Requiere revisión manual"],
        evaluated_at: new Date()
    },
    {
        transaction_id: "txn-10005",
        user_id: "John99",
        amount: 89.99,
        timestamp: new Date("2026-01-08T10:35:00Z"),
        merchant: "Grocery Store",
        is_fraudulent: false,
        risk_score: 0.10,
        decision: "approved",
        reasons: ["Transacción habitual"],
        evaluated_at: new Date()
    },
    {
        transaction_id: "txn-10006",
        user_id: "user-001",
        amount: 3200.00,
        timestamp: new Date("2026-01-08T10:40:00Z"),
        merchant: "Luxury Goods",
        is_fraudulent: true,
        risk_score: 0.95,
        decision: "rejected",
        reasons: ["Monto muy alto", "Patrón inusual"],
        evaluated_at: new Date()
    },
    {
        transaction_id: "txn-10007",
        user_id: "Maria123",
        amount: 550.00,
        timestamp: new Date("2026-01-08T10:45:00Z"),
        merchant: "Restaurant",
        is_fraudulent: false,
        risk_score: 0.20,
        decision: "approved",
        reasons: ["Monto aceptable"],
        evaluated_at: new Date()
    },
    {
        transaction_id: "txn-10008",
        user_id: "Paula05",
        amount: 1250.00,
        timestamp: new Date("2026-01-08T10:50:00Z"),
        merchant: "Fashion Store",
        is_fraudulent: false,
        risk_score: 0.35,
        decision: "approved",
        reasons: ["Dentro de límites normales"],
        evaluated_at: new Date()
    },
    {
        transaction_id: "txn-10009",
        user_id: "user-002",
        amount: 4500.00,
        timestamp: new Date("2026-01-08T10:55:00Z"),
        merchant: "Tech Store",
        is_fraudulent: true,
        risk_score: 0.90,
        decision: "rejected",
        reasons: ["Monto excesivo", "Comportamiento anómalo"],
        evaluated_at: new Date()
    },
    {
        transaction_id: "txn-10010",
        user_id: "John99",
        amount: 67.50,
        timestamp: new Date("2026-01-08T11:00:00Z"),
        merchant: "Gas Station",
        is_fraudulent: false,
        risk_score: 0.08,
        decision: "approved",
        reasons: ["Transacción típica"],
        evaluated_at: new Date()
    },
    {
        transaction_id: "txn-10011",
        user_id: "Maria123",
        amount: 1650.00,
        timestamp: new Date("2026-01-08T11:05:00Z"),
        merchant: "Hotel Booking",
        is_fraudulent: false,
        risk_score: 0.40,
        decision: "approved",
        reasons: ["Reserva hotel normal"],
        evaluated_at: new Date()
    },
    {
        transaction_id: "txn-10012",
        user_id: "Paula05",
        amount: 2100.00,
        timestamp: new Date("2026-01-08T11:10:00Z"),
        merchant: "Electronics",
        is_fraudulent: true,
        risk_score: 0.80,
        decision: "manual_review",
        reasons: ["Monto elevado", "Revisión requerida"],
        evaluated_at: new Date()
    },
    {
        transaction_id: "txn-10013",
        user_id: "user-003",
        amount: 345.00,
        timestamp: new Date("2026-01-08T11:15:00Z"),
        merchant: "Pharmacy",
        is_fraudulent: false,
        risk_score: 0.12,
        decision: "approved",
        reasons: ["Compra normal"],
        evaluated_at: new Date()
    },
    {
        transaction_id: "txn-10014",
        user_id: "John99",
        amount: 5200.00,
        timestamp: new Date("2026-01-08T11:20:00Z"),
        merchant: "Furniture Store",
        is_fraudulent: true,
        risk_score: 0.92,
        decision: "rejected",
        reasons: ["Monto extremadamente alto", "Alto riesgo"],
        evaluated_at: new Date()
    },
    {
        transaction_id: "txn-10015",
        user_id: "Maria123",
        amount: 156.75,
        timestamp: new Date("2026-01-08T11:25:00Z"),
        merchant: "Bookstore",
        is_fraudulent: false,
        risk_score: 0.09,
        decision: "approved",
        reasons: ["Compra habitual"],
        evaluated_at: new Date()
    }
];

db.fraud_evaluations.insertMany(evaluations);

// También insertar en evaluations para compatibilidad
db.evaluations.insertMany(evaluations);

// Insertar audit logs
const auditLogs = evaluations.map(ev => ({
    action: "fraud_evaluation",
    transaction_id: ev.transaction_id,
    user_id: ev.user_id,
    details: {
        decision: ev.decision,
        risk_score: ev.risk_score,
        is_fraudulent: ev.is_fraudulent
    },
    timestamp: ev.evaluated_at
}));

db.audit_logs.insertMany(auditLogs);

print("Datos insertados exitosamente!");
print("Total evaluaciones: " + db.fraud_evaluations.countDocuments());
print("Total audit logs: " + db.audit_logs.countDocuments());
