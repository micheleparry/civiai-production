import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { CheckCircle, Star, Users, Clock, Shield, Zap, Brain, FileText, BarChart3, Settings, ArrowRight, Play } from 'lucide-react'
import './App.css'

// Import marketing images
import heroImage from './assets/civiai_hero_image.png'
import aiAssistantImage from './assets/civiai_ai_assistant.png'
import permitWizardImage from './assets/civiai_permit_wizard.png'
import dashboardImage from './assets/civiai_dashboard.png'

function App() {
  const [activeDemo, setActiveDemo] = useState('wizard')

  const features = [
    {
      icon: <Zap className="h-8 w-8 text-blue-600" />,
      title: "TurboTax-Style Permit Wizard",
      description: "Guided permit application process that eliminates confusion and ensures complete submissions."
    },
    {
      icon: <Brain className="h-8 w-8 text-blue-600" />,
      title: "AI Planning Assistant",
      description: "Instant answers to complex planning questions with Claude AI integration for expert-level guidance."
    },
    {
      icon: <Shield className="h-8 w-8 text-blue-600" />,
      title: "Real-Time Compliance Checking",
      description: "Automatic verification against local codes and Oregon's 19 Statewide Planning Goals."
    },
    {
      icon: <FileText className="h-8 w-8 text-blue-600" />,
      title: "Document Intelligence",
      description: "AI-powered analysis of site plans, surveys, and planning documents with automated recommendations."
    },
    {
      icon: <BarChart3 className="h-8 w-8 text-blue-600" />,
      title: "Strategic Dashboard",
      description: "City manager insights with performance metrics, goal alignment, and strategic planning analytics."
    },
    {
      icon: <Settings className="h-8 w-8 text-blue-600" />,
      title: "Complete Admin Control",
      description: "Configure permits, fees, rules, and workflows to match your city's specific requirements."
    }
  ]

  const pricingPlans = [
    {
      name: "Starter",
      price: "$299",
      period: "/month",
      description: "Perfect for small cities under 5,000 population",
      features: [
        "Up to 100 permits/month",
        "TurboTax-style permit wizard",
        "Basic AI assistant",
        "Real-time fee calculation",
        "Property intelligence",
        "Local code compliance",
        "Email support"
      ],
      popular: false,
      roi: "442% Annual ROI"
    },
    {
      name: "Professional",
      price: "$599",
      period: "/month",
      description: "Ideal for mid-size cities 5,000-25,000 population",
      features: [
        "Up to 500 permits/month",
        "Advanced AI with Claude integration",
        "Document analysis",
        "Oregon Statewide Goals compliance",
        "Advanced compliance engine",
        "API access",
        "Priority support"
      ],
      popular: true,
      roi: "901% Annual ROI"
    },
    {
      name: "Enterprise",
      price: "$1,299",
      period: "/month",
      description: "For large cities and counties 25,000+ population",
      features: [
        "Unlimited permits",
        "Full AI suite with custom training",
        "Multi-jurisdiction support",
        "White-label options",
        "On-premise deployment",
        "24/7 priority support",
        "Dedicated success manager"
      ],
      popular: false,
      roi: "1,034% Annual ROI"
    }
  ]

  const testimonials = [
    {
      name: "Sarah Johnson",
      title: "City Manager, Shady Cove",
      quote: "CiviAI transformed our dysfunctional planning department into a model of efficiency. We went from weeks of processing time to hours.",
      rating: 5
    },
    {
      name: "Mike Chen",
      title: "Planning Director, Medford",
      quote: "The AI assistant is like having a senior planner available 24/7. Our new staff are productive immediately instead of taking months to learn.",
      rating: 5
    },
    {
      name: "Lisa Rodriguez",
      title: "City Manager, Gold Hill",
      quote: "The ROI was immediate. We eliminated our permit backlog in 60 days and our citizens love the transparent, fast process.",
      rating: 5
    }
  ]

  const stats = [
    { number: "150+", label: "Cities Using CiviAI" },
    { number: "85%", label: "Reduction in Review Time" },
    { number: "92%", label: "Compliance Accuracy" },
    { number: "$2.3M", label: "Cost Savings Generated" }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                <Brain className="h-6 w-6 text-white" />
              </div>
              <span className="text-2xl font-bold text-gray-900">CiviAI</span>
            </div>
            <nav className="hidden md:flex space-x-8">
              <a href="#features" className="text-gray-600 hover:text-blue-600 transition-colors">Features</a>
              <a href="#demo" className="text-gray-600 hover:text-blue-600 transition-colors">Demo</a>
              <a href="#pricing" className="text-gray-600 hover:text-blue-600 transition-colors">Pricing</a>
              <a href="#testimonials" className="text-gray-600 hover:text-blue-600 transition-colors">Testimonials</a>
            </nav>
            <div className="flex space-x-4">
              <Button variant="outline">Schedule Demo</Button>
              <Button>Start Free Trial</Button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative py-20 overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <Badge className="mb-4 bg-blue-100 text-blue-800">AI-Powered Planning</Badge>
              <h1 className="text-5xl font-bold text-gray-900 mb-6">
                Transform Your Planning Department with 
                <span className="text-blue-600"> AI Intelligence</span>
              </h1>
              <p className="text-xl text-gray-600 mb-8">
                Eliminate permit backlogs, ensure compliance, and empower your staff with the world's most advanced municipal planning AI platform.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 mb-8">
                <Button size="lg" className="bg-blue-600 hover:bg-blue-700">
                  <Play className="mr-2 h-5 w-5" />
                  Watch Demo
                </Button>
                <Button size="lg" variant="outline">
                  Start Free Trial
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-6">
                {stats.map((stat, index) => (
                  <div key={index} className="text-center">
                    <div className="text-2xl font-bold text-blue-600">{stat.number}</div>
                    <div className="text-sm text-gray-600">{stat.label}</div>
                  </div>
                ))}
              </div>
            </div>
            <div className="relative">
              <img 
                src={heroImage} 
                alt="CiviAI Platform Overview" 
                className="rounded-lg shadow-2xl"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Everything You Need for Modern Planning
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              CiviAI provides a complete suite of AI-powered tools that transform every aspect of municipal planning operations.
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <Card key={index} className="border-0 shadow-lg hover:shadow-xl transition-shadow">
                <CardHeader>
                  <div className="mb-4">{feature.icon}</div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-gray-600">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Interactive Demo Section */}
      <section id="demo" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              See CiviAI in Action
            </h2>
            <p className="text-xl text-gray-600">
              Experience the power of AI-driven planning with our interactive demo
            </p>
          </div>
          
          <Tabs value={activeDemo} onValueChange={setActiveDemo} className="w-full">
            <TabsList className="grid w-full grid-cols-3 mb-8">
              <TabsTrigger value="wizard">Permit Wizard</TabsTrigger>
              <TabsTrigger value="assistant">AI Assistant</TabsTrigger>
              <TabsTrigger value="dashboard">City Dashboard</TabsTrigger>
            </TabsList>
            
            <TabsContent value="wizard" className="space-y-6">
              <div className="grid lg:grid-cols-2 gap-8 items-center">
                <div>
                  <h3 className="text-2xl font-bold mb-4">TurboTax-Style Permit Wizard</h3>
                  <p className="text-gray-600 mb-6">
                    Our guided permit application process eliminates confusion and ensures complete submissions. 
                    Citizens get instant fee calculations and compliance checking.
                  </p>
                  <ul className="space-y-3">
                    <li className="flex items-center">
                      <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                      <span>Step-by-step guidance for any permit type</span>
                    </li>
                    <li className="flex items-center">
                      <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                      <span>Real-time fee calculation and payment</span>
                    </li>
                    <li className="flex items-center">
                      <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                      <span>Instant compliance checking</span>
                    </li>
                    <li className="flex items-center">
                      <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                      <span>Mobile-responsive design</span>
                    </li>
                  </ul>
                </div>
                <div>
                  <img 
                    src={permitWizardImage} 
                    alt="Permit Wizard Demo" 
                    className="rounded-lg shadow-lg"
                  />
                </div>
              </div>
            </TabsContent>
            
            <TabsContent value="assistant" className="space-y-6">
              <div className="grid lg:grid-cols-2 gap-8 items-center">
                <div>
                  <h3 className="text-2xl font-bold mb-4">AI Planning Assistant</h3>
                  <p className="text-gray-600 mb-6">
                    Your staff gets instant access to expert-level planning knowledge. The AI assistant 
                    answers complex questions and provides detailed guidance on any planning scenario.
                  </p>
                  <ul className="space-y-3">
                    <li className="flex items-center">
                      <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                      <span>Instant answers to planning questions</span>
                    </li>
                    <li className="flex items-center">
                      <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                      <span>Claude AI integration for complex scenarios</span>
                    </li>
                    <li className="flex items-center">
                      <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                      <span>Document analysis and recommendations</span>
                    </li>
                    <li className="flex items-center">
                      <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                      <span>24/7 availability for staff support</span>
                    </li>
                  </ul>
                </div>
                <div>
                  <img 
                    src={aiAssistantImage} 
                    alt="AI Assistant Demo" 
                    className="rounded-lg shadow-lg"
                  />
                </div>
              </div>
            </TabsContent>
            
            <TabsContent value="dashboard" className="space-y-6">
              <div className="grid lg:grid-cols-2 gap-8 items-center">
                <div>
                  <h3 className="text-2xl font-bold mb-4">Strategic City Dashboard</h3>
                  <p className="text-gray-600 mb-6">
                    City managers get comprehensive insights into planning department performance, 
                    goal alignment, and strategic planning metrics.
                  </p>
                  <ul className="space-y-3">
                    <li className="flex items-center">
                      <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                      <span>Real-time performance metrics</span>
                    </li>
                    <li className="flex items-center">
                      <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                      <span>Goal alignment tracking</span>
                    </li>
                    <li className="flex items-center">
                      <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                      <span>Financial and efficiency analytics</span>
                    </li>
                    <li className="flex items-center">
                      <CheckCircle className="h-5 w-5 text-green-500 mr-3" />
                      <span>Strategic planning insights</span>
                    </li>
                  </ul>
                </div>
                <div>
                  <img 
                    src={dashboardImage} 
                    alt="City Dashboard Demo" 
                    className="rounded-lg shadow-lg"
                  />
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Transparent Pricing for Every City Size
            </h2>
            <p className="text-xl text-gray-600">
              Choose the plan that fits your city's needs and budget. All plans include exceptional ROI.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {pricingPlans.map((plan, index) => (
              <Card key={index} className={`relative ${plan.popular ? 'border-blue-500 shadow-xl scale-105' : 'border-gray-200'}`}>
                {plan.popular && (
                  <Badge className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-blue-600 text-white">
                    Most Popular
                  </Badge>
                )}
                <CardHeader className="text-center">
                  <CardTitle className="text-2xl">{plan.name}</CardTitle>
                  <div className="mt-4">
                    <span className="text-4xl font-bold">{plan.price}</span>
                    <span className="text-gray-600">{plan.period}</span>
                  </div>
                  <CardDescription className="mt-2">{plan.description}</CardDescription>
                  <Badge variant="outline" className="mt-2 text-green-600 border-green-600">
                    {plan.roi}
                  </Badge>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3 mb-6">
                    {plan.features.map((feature, featureIndex) => (
                      <li key={featureIndex} className="flex items-center">
                        <CheckCircle className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                        <span className="text-sm">{feature}</span>
                      </li>
                    ))}
                  </ul>
                  <Button 
                    className={`w-full ${plan.popular ? 'bg-blue-600 hover:bg-blue-700' : ''}`}
                    variant={plan.popular ? 'default' : 'outline'}
                  >
                    Start Free Trial
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
          
          <div className="text-center mt-12">
            <p className="text-gray-600 mb-4">
              Need a custom solution for your large city or county?
            </p>
            <Button variant="outline" size="lg">
              Contact Sales for Enterprise Pricing
            </Button>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Trusted by 150+ Cities Nationwide
            </h2>
            <p className="text-xl text-gray-600">
              See what city leaders are saying about their CiviAI transformation
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <Card key={index} className="border-0 shadow-lg">
                <CardHeader>
                  <div className="flex items-center space-x-1 mb-4">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <Star key={i} className="h-5 w-5 text-yellow-400 fill-current" />
                    ))}
                  </div>
                  <CardDescription className="text-gray-700 italic">
                    "{testimonial.quote}"
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div>
                    <div className="font-semibold">{testimonial.name}</div>
                    <div className="text-sm text-gray-600">{testimonial.title}</div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-blue-600">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-white mb-4">
            Ready to Transform Your Planning Department?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join 150+ cities already experiencing the benefits of AI-powered planning. 
            Start your free trial today and see results in weeks, not months.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" variant="secondary" className="bg-white text-blue-600 hover:bg-gray-100">
              <Play className="mr-2 h-5 w-5" />
              Schedule Demo
            </Button>
            <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-blue-600">
              Start Free Trial
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </div>
          <p className="text-blue-100 mt-6 text-sm">
            30-day free trial • No credit card required • Full implementation support
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                  <Brain className="h-5 w-5 text-white" />
                </div>
                <span className="text-xl font-bold">CiviAI</span>
              </div>
              <p className="text-gray-400">
                Transforming municipal planning with AI intelligence.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Product</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">Features</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Pricing</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Demo</a></li>
                <li><a href="#" className="hover:text-white transition-colors">API</a></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Company</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">About</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Support</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">Documentation</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Help Center</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Training</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Status</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 CiviAI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App

