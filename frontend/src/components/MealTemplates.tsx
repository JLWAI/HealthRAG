import { useState } from 'react'
import { Plus, Clock, Hash, Trash2, ChevronDown, ChevronUp } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useMealTemplates, useCreateTemplate, useLogTemplate, useDeleteTemplate } from '@/hooks/useApi'
import type { MealTemplate } from '@/api/client'

interface MealTemplatesProps {
  onTemplateLogged?: () => void
}

export function MealTemplates({ onTemplateLogged }: MealTemplatesProps) {
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [expandedTemplate, setExpandedTemplate] = useState<number | null>(null)
  const [sortBy, setSortBy] = useState<'recent' | 'frequent' | 'name'>('recent')

  const { data: templates, isLoading } = useMealTemplates(undefined, sortBy)
  const createTemplate = useCreateTemplate()
  const logTemplate = useLogTemplate()
  const deleteTemplate = useDeleteTemplate()

  // Form state for creating template
  const [templateName, setTemplateName] = useState('')
  const [templateMealType, setTemplateMealType] = useState<'breakfast' | 'lunch' | 'dinner' | 'snack'>('breakfast')
  const [templateDescription, setTemplateDescription] = useState('')

  const handleCreateTemplate = () => {
    if (!templateName.trim()) return

    createTemplate.mutate(
      {
        name: templateName,
        meal_type: templateMealType,
        description: templateDescription || undefined,
      },
      {
        onSuccess: () => {
          setIsCreateOpen(false)
          setTemplateName('')
          setTemplateDescription('')
        },
      }
    )
  }

  const handleLogTemplate = (id: number) => {
    logTemplate.mutate(
      { id, multiplier: 1.0 },
      {
        onSuccess: () => {
          onTemplateLogged?.()
        },
      }
    )
  }

  const handleDeleteTemplate = (id: number, name: string) => {
    if (confirm(`Delete template "${name}"?`)) {
      deleteTemplate.mutate(id)
    }
  }

  const toggleExpand = (id: number) => {
    setExpandedTemplate(expandedTemplate === id ? null : id)
  }

  if (isLoading) {
    return (
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Meal Templates</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Loading templates...</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base">Meal Templates</CardTitle>
          <div className="flex items-center gap-2">
            <Select value={sortBy} onValueChange={(v) => setSortBy(v as typeof sortBy)}>
              <SelectTrigger className="w-32 h-8">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="recent">Recent</SelectItem>
                <SelectItem value="frequent">Most Used</SelectItem>
                <SelectItem value="name">Name</SelectItem>
              </SelectContent>
            </Select>

            <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
              <DialogTrigger asChild>
                <Button size="sm" variant="outline">
                  <Plus className="h-4 w-4 mr-1" />
                  New
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create Meal Template</DialogTitle>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Template Name</Label>
                    <Input
                      id="name"
                      placeholder="e.g., Morning Shake"
                      value={templateName}
                      onChange={(e) => setTemplateName(e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="meal-type">Meal Type</Label>
                    <Select value={templateMealType} onValueChange={(v) => setTemplateMealType(v as typeof templateMealType)}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="breakfast">Breakfast</SelectItem>
                        <SelectItem value="lunch">Lunch</SelectItem>
                        <SelectItem value="dinner">Dinner</SelectItem>
                        <SelectItem value="snack">Snack</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="description">Description (optional)</Label>
                    <Input
                      id="description"
                      placeholder="e.g., Post-workout protein shake"
                      value={templateDescription}
                      onChange={(e) => setTemplateDescription(e.target.value)}
                    />
                  </div>
                  <p className="text-xs text-muted-foreground">
                    This will save all {templateMealType} foods logged today as a template.
                  </p>
                </div>
                <DialogFooter>
                  <Button onClick={handleCreateTemplate} disabled={!templateName.trim() || createTemplate.isPending}>
                    {createTemplate.isPending ? 'Creating...' : 'Create Template'}
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {!templates || templates.length === 0 ? (
          <div className="text-center py-6">
            <p className="text-sm text-muted-foreground">No templates yet</p>
            <p className="text-xs text-muted-foreground mt-1">
              Log a meal, then create a template to save it for one-click logging later
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {templates.map((template: MealTemplate) => (
              <div key={template.template_id} className="border rounded-lg p-3 space-y-2">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h4 className="font-medium">{template.name}</h4>
                      <span className="text-xs px-2 py-0.5 rounded-full bg-muted capitalize">
                        {template.meal_type}
                      </span>
                    </div>
                    {template.description && (
                      <p className="text-xs text-muted-foreground mt-1">{template.description}</p>
                    )}
                    <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {template.last_used ? `Last used ${new Date(template.last_used).toLocaleDateString()}` : 'Never used'}
                      </span>
                      <span className="flex items-center gap-1">
                        <Hash className="h-3 w-3" />
                        {template.use_count} uses
                      </span>
                    </div>
                  </div>
                  <div className="flex items-start gap-1">
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => toggleExpand(template.template_id)}
                      className="h-8 w-8 p-0"
                    >
                      {expandedTemplate === template.template_id ? (
                        <ChevronUp className="h-4 w-4" />
                      ) : (
                        <ChevronDown className="h-4 w-4" />
                      )}
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleDeleteTemplate(template.template_id, template.name)}
                      className="h-8 w-8 p-0 text-destructive"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>

                {expandedTemplate === template.template_id && (
                  <div className="pt-2 border-t space-y-2">
                    <div className="text-xs space-y-1">
                      {template.foods.map((food, idx) => (
                        <div key={idx} className="flex justify-between">
                          <span>
                            {food.servings}x {food.food_name}
                          </span>
                          <span className="text-muted-foreground">
                            {food.calories}cal, {food.protein_g}p
                          </span>
                        </div>
                      ))}
                    </div>
                    <div className="pt-2 border-t">
                      <div className="flex justify-between text-xs font-medium">
                        <span>Total:</span>
                        <span>
                          {template.total_calories}cal, {template.total_protein_g}p, {template.total_carbs_g}c,{' '}
                          {template.total_fat_g}f
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                <Button
                  size="sm"
                  onClick={() => handleLogTemplate(template.template_id)}
                  disabled={logTemplate.isPending}
                  className="w-full"
                >
                  {logTemplate.isPending ? 'Logging...' : `Log to Today (${template.total_calories}cal)`}
                </Button>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
