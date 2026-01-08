import { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { getRules, updateRule, createRule, deleteRule } from '@/services/api';
import type { Rule } from '@/types';

export default function RulesPage() {
  const [rules, setRules] = useState<Rule[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingRule, setEditingRule] = useState<Rule | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [newRule, setNewRule] = useState({
    name: '',
    type: 'custom',
    parameters: {},
    enabled: true,
    order: 999
  });
  const [parametersText, setParametersText] = useState('{}');

  useEffect(() => {
    loadRules();
  }, []);

  const loadRules = async () => {
    try {
      const data = await getRules();
      setRules(data);
    } catch (error) {
      toast.error('Error al cargar reglas');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleEditRule = (rule: Rule) => {
    setEditingRule(rule);
  };

  const handleSaveRule = async () => {
    if (!editingRule) return;
    
    try {
      await updateRule(editingRule.id, editingRule.parameters);
      toast.success('Regla actualizada exitosamente');
      setEditingRule(null);
      loadRules();
    } catch (error) {
      toast.error('Error al actualizar regla');
      console.error(error);
    }
  };

  const handleCreateRule = async () => {
    if (!newRule.name || !newRule.type) {
      toast.error('Por favor completa todos los campos requeridos');
      return;
    }
    
    // Validar que el JSON sea válido
    try {
      JSON.parse(parametersText);
    } catch {
      toast.error('El formato de parámetros JSON es inválido');
      return;
    }
    
    try {
      const result = await createRule(newRule);
      console.log('Regla creada:', result);
      toast.success('Regla creada exitosamente');
      setIsCreating(false);
      setNewRule({
        name: '',
        type: 'custom',
        parameters: {},
        enabled: true,
        order: 999
      });
      setParametersText('{}');
      loadRules();
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Error al crear regla');
      console.error('Error creando regla:', error);
    }
  };

  const handleDeleteRule = async (ruleId: string, ruleName: string) => {
    if (!confirm(`¿Estás seguro de eliminar la regla "${ruleName}"?`)) {
      return;
    }
    
    try {
      await deleteRule(ruleId);
      toast.success('Regla eliminada exitosamente');
      loadRules();
    } catch (error: any) {
      const message = error?.response?.data?.detail || 'Error al eliminar regla';
      toast.error(message);
      console.error('Error eliminando regla:', error);
    }
  };

  if (loading) {
    return <div className="text-gray-400">Cargando...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Reglas de Fraude</h1>
        <button
          onClick={() => setIsCreating(true)}
          className="px-6 py-2 bg-green-600 rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
        >
          <span className="text-xl">+</span>
          Nueva Regla
        </button>
      </div>

      <div className="space-y-4">
        {rules.map((rule) => (
          <div key={rule.id} className="bg-admin-surface rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">{rule.name}</h3>
              <div className="flex gap-2">
                <button
                  onClick={() => handleEditRule(rule)}
                  className="px-4 py-2 bg-admin-primary rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  Editar
                </button>
                <button
                  onClick={() => handleDeleteRule(rule.id, rule.name)}
                  className="px-4 py-2 bg-red-600 rounded-lg hover:bg-red-700 transition-colors"
                >
                  Eliminar
                </button>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-400">Tipo:</span>
                <span className="ml-2 text-white">{rule.type}</span>
              </div>
              <div>
                <span className="text-gray-400">Prioridad:</span>
                <span className="ml-2 text-white">{rule.order}</span>
              </div>
              <div className="col-span-2">
                <span className="text-gray-400">Parámetros:</span>
                <pre className="mt-2 p-3 bg-admin-bg rounded-lg text-xs">
                  {JSON.stringify(rule.parameters, null, 2)}
                </pre>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Modal de Edición */}
      {editingRule && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-admin-surface rounded-xl p-8 max-w-md w-full">
            <h2 className="text-xl font-bold mb-6">Editar Regla: {editingRule.name}</h2>
            <div className="space-y-4">
              {editingRule.type === 'amount_threshold' && (
                <div>
                  <label className="block text-sm mb-2">Threshold ($)</label>
                  <input
                    type="number"
                    className="w-full px-4 py-2 bg-admin-bg rounded-lg border border-gray-600 focus:border-admin-primary focus:outline-none"
                    value={editingRule.parameters.threshold}
                    onChange={(e) =>
                      setEditingRule({
                        ...editingRule,
                        parameters: { ...editingRule.parameters, threshold: parseFloat(e.target.value) },
                      })
                    }
                  />
                </div>
              )}
              {editingRule.type === 'location_check' && (
                <div>
                  <label className="block text-sm mb-2">Radio (km)</label>
                  <input
                    type="number"
                    className="w-full px-4 py-2 bg-admin-bg rounded-lg border border-gray-600 focus:border-admin-primary focus:outline-none"
                    value={editingRule.parameters.radius_km}
                    onChange={(e) =>
                      setEditingRule({
                        ...editingRule,
                        parameters: { ...editingRule.parameters, radius_km: parseFloat(e.target.value) },
                      })
                    }
                  />
                </div>
              )}
            </div>
            <div className="flex space-x-4 mt-6">
              <button
                onClick={() => setEditingRule(null)}
                className="flex-1 px-4 py-2 bg-gray-600 rounded-lg hover:bg-gray-700 transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleSaveRule}
                className="flex-1 px-4 py-2 bg-admin-primary rounded-lg hover:bg-indigo-700 transition-colors"
              >
                Guardar Cambios
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Creación */}
      {isCreating && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-admin-surface rounded-xl p-8 max-w-md w-full">
            <h2 className="text-xl font-bold mb-6">Crear Nueva Regla</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm mb-2">Nombre de la Regla *</label>
                <input
                  type="text"
                  className="w-full px-4 py-2 bg-admin-bg rounded-lg border border-gray-600 focus:border-admin-primary focus:outline-none"
                  placeholder="Ej: Regla de horario nocturno"
                  value={newRule.name}
                  onChange={(e) => setNewRule({ ...newRule, name: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm mb-2">Tipo de Regla *</label>
                <select
                  className="w-full px-4 py-2 bg-admin-bg rounded-lg border border-gray-600 focus:border-admin-primary focus:outline-none"
                  value={newRule.type}
                  onChange={(e) => setNewRule({ ...newRule, type: e.target.value })}
                >
                  <option value="custom">Regla Personalizada</option>
                  <option value="amount_threshold">Umbral de Monto</option>
                  <option value="location_check">Verificación de Ubicación</option>
                  <option value="time_based">Basada en Horario</option>
                  <option value="frequency">Frecuencia de Transacciones</option>
                  <option value="velocity">Velocidad de Transacciones</option>
                </select>
              </div>
              <div>
                <label className="block text-sm mb-2">Parámetros (JSON)</label>
                <textarea
                  className="w-full px-4 py-2 bg-admin-bg rounded-lg border border-gray-600 focus:border-admin-primary focus:outline-none font-mono text-sm"
                  rows={4}
                  placeholder='{\n  "threshold": 1000,\n  "action": "flag"\n}'
                  value={parametersText}
                  onChange={(e) => {
                    const text = e.target.value;
                    setParametersText(text);
                    // Intentar parsear solo para validar
                    try {
                      const params = JSON.parse(text);
                      setNewRule({ ...newRule, parameters: params });
                    } catch {
                      // JSON inválido, pero permitir que el usuario siga escribiendo
                    }
                  }}
                />
                {(() => {
                  try {
                    JSON.parse(parametersText);
                    return <p className="text-xs text-green-400 mt-1">✓ JSON válido</p>;
                  } catch {
                    return <p className="text-xs text-yellow-400 mt-1">⚠ JSON inválido</p>;
                  }
                })()}
              </div>
              <div>
                <label className="block text-sm mb-2">Prioridad (orden)</label>
                <input
                  type="number"
                  className="w-full px-4 py-2 bg-admin-bg rounded-lg border border-gray-600 focus:border-admin-primary focus:outline-none"
                  value={newRule.order}
                  onChange={(e) => setNewRule({ ...newRule, order: parseInt(e.target.value) })}
                />
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="enabled"
                  className="mr-2"
                  checked={newRule.enabled}
                  onChange={(e) => setNewRule({ ...newRule, enabled: e.target.checked })}
                />
                <label htmlFor="enabled" className="text-sm">Regla activa</label>
              </div>
            </div>
            <div className="flex space-x-4 mt-6">
              <button
                onClick={() => {
                  setIsCreating(false);
                  setNewRule({
                    name: '',
                    type: 'custom',
                    parameters: {},
                    enabled: true,
                    order: 999
                  });
                  setParametersText('{}');
                }}
                className="flex-1 px-4 py-2 bg-gray-600 rounded-lg hover:bg-gray-700 transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleCreateRule}
                className="flex-1 px-4 py-2 bg-green-600 rounded-lg hover:bg-green-700 transition-colors"
              >
                Crear Regla
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
